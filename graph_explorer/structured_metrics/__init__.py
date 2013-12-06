import os
import sys
import imp
import re
from inspect import isclass
import sre_constants
import logging
import json
sys.path.append("%s/%s" % (os.path.dirname(os.path.realpath(__file__)), 'elasticsearch-py'))
sys.path.append("%s/%s" % (os.path.dirname(os.path.realpath(__file__)), 'urllib3'))

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import TransportError


query_all = {
    "query_string": {
        "query": "*"
    }
}


def es_query(query, k, v):
    return {
        'query': {
            query: {
                k: v
            }
        }
    }


def es_regexp(k, v):
    return {
        'regexp': {
            k: v
        }
    }


def es_prefix(k, v):
    return {
        'prefix': {
            k: v
        }
    }


def hit_to_metric(hit):
    tags = {}
    for tag in hit['_source']['tags']:
        (k, v) = tag.split('=', 1)
        tags[str(k)] = str(v)
    return {
        'id': hit['_id'],
        'tags': tags
    }


class PluginError(Exception):

    def __init__(self, plugin, msg, underlying_error):
        Exception.__init__(self, msg)
        self.plugin = plugin
        self.msg = msg
        self.underlying_error = underlying_error

    def __str__(self):
        return "%s -> %s (%s)" % (self.plugin, self.msg, self.underlying_error)


def regex_unanchor(regexp):
    """
    ES regexps are anchored, so adding .* is necessary at the beginning and
    end to get a substring match. But we want to skip that if front/end
    anchors are explicitly used.

    Also avoid doubling up wildcards, in case the regexp engine is not smart
    about backtracking.
    """

    if regexp.startswith('^'):
        regexp = regexp.lstrip('^')
    elif not regexp.startswith('.*'):
        regexp = '.*' + regexp
    if regexp.endswith('$'):
        regexp = regexp.rstrip('$')
    elif not regexp.endswith('.*'):
        regexp += '.*'
    return regexp


def build_es_match_tag_equality(key, term):
    return es_query('match', 'tags', '%s=%s' % (key, term))


def build_es_match_tag_exists(key):
    return es_prefix('tags', key + '=')


def build_es_match_any_tag_value(term):
    return es_regexp('tags', ".*=" + re.escape(term))


def build_es_match_tag_regex(key, term):
    return es_regexp('tags', '%s=%s' % (re.escape(key), regex_unanchor(term)))


def build_es_match_tag_name_regex(key):
    return es_regexp('tags', '%s=.*' % regex_unanchor(key))


def build_es_match_tag_value_regex(term):
    return es_regexp('tags', '.*=%s' % regex_unanchor(term))


def build_es_match_id_regex(key):
    # here 'id' is to be interpreted loosely, as in the old
    # (python-native datastructures) approach where we used
    # Plugin.get_target_id to have an id that contains the graphite
    # metric, but also the tags etc. so if the user types just a
    # word, we want the metrics to be returned where the id or tags
    # are matched
    return {'or': [es_regexp('_id', regex_unanchor(key)),
                   es_regexp('tags', regex_unanchor(key))]}


def build_es_match_negate(ast):
    return {'not': build_es_expr(ast)}


def build_es_match_or(*asts):
    return {'or': map(build_es_expr, asts)}


def build_es_match_and(*asts):
    return {'and': map(build_es_expr, asts)}


def build_es_expr(ast):
    return globals()['build_es_' + ast[0]](*ast[1:])


def build_es_query(ast):
    return {
        "filtered": {
            "query": {"match_all": {}},
            "filter": build_es_expr(ast)
        }
    }


class StructuredMetrics(object):

    def __init__(self, config, logger=logging):
        self.plugins = []
        es_host = config.es_host.replace('http://', '').replace('https://', '')
        self.es = Elasticsearch([{"host": es_host, "port": config.es_port}])
        self.logger = logger
        self.config = config

    def load_plugins(self):
        '''
        loads all the plugins sub-modules
        returns encountered errors, doesn't raise them because
        whoever calls this function defines how any errors are
        handled. meanwhile, loading must continue
        '''
        from . import plugins
        errors = []
        plugin_dirs = getattr(self.config, "metric_plugin_dirs", ('**builtins**',))
        for plugin_dir in plugin_dirs:
            if plugin_dir == '**builtins**':
                plugin_dir = os.path.dirname(plugins.__file__)
            newplugins, newerrors = self.load_plugins_from(plugin_dir, plugins)
            self.plugins.extend(newplugins)
            errors.extend(newerrors)
        return errors

    @staticmethod
    def load_plugins_from(plugin_dir, package):
        # import in sorted order to let it be predictable; lets user plugins import
        # pieces of other plugins imported earlier
        plugins = []
        errors = []
        Plugin = package.Plugin
        for f in sorted(os.listdir(plugin_dir)):
            if f == '__init__.py' or not f.endswith(".py"):
                continue
            mname = f[:-3]
            qualifiedname = package.__name__ + '.' + mname
            imp.acquire_lock()
            try:
                module = imp.load_source(qualifiedname, os.path.join(plugin_dir, f))
                sys.modules[qualifiedname] = module
                setattr(package, mname, module)
            except Exception, e:  # pylint: disable=W0703
                errors.append(PluginError(mname, "Failed to add plugin '%s'" % mname, e))
                continue
            finally:
                imp.release_lock()
            for item in vars(module).itervalues():
                if isclass(item) and item != Plugin and issubclass(item, Plugin):
                    try:
                        plugins.append((mname, item()))
                    # regex error is too vague to stand on its own
                    except sre_constants.error, e:
                        e = "error problem parsing matching regex: %s" % e
                        errors.append(PluginError(mname, "Failed to add plugin '%s'" % mname, e))
                    except Exception, e:  # pylint: disable=W0703
                        errors.append(PluginError(mname, "Failed to add plugin '%s'" % mname, e))
        # sort plugins by their matching priority
        return sorted(plugins, key=lambda t: t[1].priority, reverse=True), errors

    def list_metrics(self, metrics):
        for plugin in self.plugins:
            (plugin_name, plugin_object) = plugin
            plugin_object.reset_target_yield_counters()
        targets = {}
        plugin_stats = {}
        for plugin in self.plugins:
            plugin_stats[plugin[0]] = 0
        for metric in metrics:
            for plugin in self.plugins:
                (plugin_name, plugin_object) = plugin
                proto2_metric = plugin_object.upgrade_metric(metric)
                if proto2_metric is not None:
                    (k, v) = proto2_metric
                    tags = v['tags']
                    if 'target_type' not in tags or ('unit' not in tags and 'what' not in tags):
                        self.logger.warn("metric '%s' doesn't have the mandatory tags "
                                         "('target_type' and either 'unit' or 'what').  "
                                         "ignoring it...", v)
                    else:
                        # old style tags: what, target_type
                        # new style: unit, (and target_type, for now)
                        # automatically convert
                        if 'unit' not in tags and 'what' in tags:
                            convert = {
                                'bytes': 'B',
                                'bits': 'b'
                            }
                            unit = convert.get(tags['what'], tags['what'])
                            if tags['target_type'] is 'rate':
                                v['tags']['unit'] = '%s/s' % unit
                            else:
                                v['tags']['unit'] = unit
                            del v['tags']['what']
                        targets[k] = v
                        plugin_stats[plugin_name] += 1
                        break
        for plugin in self.plugins:
            plugin_name = plugin[0]
            self.logger.debug("plugin %20s upgraded %10d metrics to proto2", plugin_name, plugin_stats[plugin_name])
        return targets

    def es_bulk(self, bulk_list):
        if not len(bulk_list):
            return
        body = '\n'.join(map(json.dumps, bulk_list)) + '\n'
        self.es.bulk(index='graphite_metrics', doc_type='metric', body=body)

    def assure_index(self):
        body = {
            "settings": {
                "number_of_shards": 1
            },
            "mappings": {
                "metric": {
                    "_source": {"enabled": True},
                    "_id": {"index": "not_analyzed", "store": "yes"},
                    "properties": {
                        "tags": {"type": "string", "index": "not_analyzed"}
                    }
                }
            }
        }
        self.logger.debug("making sure index exists..")
        try:
            self.es.indices.create(index='graphite_metrics', body=body)
        except TransportError, e:
            if 'IndexAlreadyExistsException' in e[1]:
                pass
            else:
                raise

        self.logger.debug("making sure shard is started..")
        # not sure what happens when this times out, an exception maybe?
        self.es.cluster.health(index='graphite_metrics', wait_for_status='yellow')
        self.logger.debug("shard is ready!")

    def remove_metrics_not_in(self, metrics):
        bulk_size = 1000
        bulk_list = []
        affected = 0
        self.assure_index()
        index = set(metrics)
        for es_metrics in self.get_all_metrics():
            for hit in es_metrics['hits']['hits']:
                if hit['_id'] not in index:
                    bulk_list.append({'delete': {'_id': hit['_id']}})
                    affected += 1
                    if len(bulk_list) >= bulk_size:
                        self.es_bulk(bulk_list)
                        bulk_list = []
        self.es_bulk(bulk_list)
        self.logger.debug("removed %d metrics from elasticsearch", affected)

    def update_targets(self, metrics):
        # using >1 threads/workers/connections would make this faster
        bulk_size = 1000
        bulk_list = []
        affected = 0
        targets = self.list_metrics(metrics)

        self.assure_index()

        for target in targets.values():
            bulk_list.append({'index': {'_id': target['id']}})
            bulk_list.append({'tags': ['%s=%s' % tuple(tag) for tag in target['tags'].items()]})
            affected += 1
            if len(bulk_list) >= bulk_size:
                self.es_bulk(bulk_list)
                bulk_list = []
        self.es_bulk(bulk_list)
        self.logger.debug("indexed %d metrics", affected)

    def load_metric(self, metric_id):
        hit = self.get(metric_id)
        return hit_to_metric(hit)

    def count_metrics(self):
        self.assure_index()
        ret = self.es.count(index='graphite_metrics', doc_type='metric')
        return ret['count']

    def get_metrics(self, query=None, size=1000):
        self.assure_index()
        self.logger.debug("Sending query to ES: %r", query)
        try:
            if query is None:
                query = query_all
            return self.es.search(index='graphite_metrics', doc_type='metric', size=size, body={
                "query": query,
            })
        except Exception, e:  # pylint: disable=W0703
            sys.stderr.write("Could not connect to ElasticSearch: %s" % e)

    def get_all_metrics(self, query=None, size=200):
        self.assure_index()
        try:
            if query is None:
                query = query_all
            d = self.es.search(index='graphite_metrics', doc_type='metric', size=size,
                               search_type='scan', scroll='10m', body={"query": query})
            scroll_id = d['_scroll_id']
            d = None
            while (d is None or len(d['hits']['hits'])):
                d = self.es.scroll(scroll='10m', scroll_id=scroll_id)
                yield d
                scroll_id = d['_scroll_id']
        except Exception, e:  # pylint: disable=W0703
            sys.stderr.write("Could not connect to ElasticSearch: %s" % e)

    def get(self, metric_id):
        self.assure_index()
        return self.es.get(index='graphite_metrics', doc_type='metric', id=metric_id)

    def matching(self, query):
        self.assure_index()
        if query['sum_by'] or query['avg_by']:
            # user requested aggregation, so we must make sure there's enough
            # metrics to have enough ($limit or more) targets after aggregation
            limit_es = query['limit_targets'] * 1000
        else:
            # no aggregation, so fetching $limit targets is enough
            limit_es = query['limit_targets']
        limit_es = min(self.config.limit_es_metrics, limit_es)
        self.logger.debug("querying up to %d metrics from ES...", limit_es)
        my_es_query = build_es_query(query['ast'])
        metrics = self.get_metrics(my_es_query, limit_es)
        self.logger.debug("got %d metrics!", len(metrics))
        results = {}
        for hit in metrics['hits']['hits']:
            metric = hit_to_metric(hit)
            results[metric['id']] = metric
        query['limit_es'] = limit_es
        return (query, results)
