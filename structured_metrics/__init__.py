import os
import sys
from inspect import isclass
import sre_constants
import logging
import time
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        raise ImportError("GE requires python2, 2.6 or higher, or 2.5 with simplejson.")
sys.path.append("%s/%s" % (os.path.dirname(os.path.realpath(__file__)), 'requests'))
sys.path.append("%s/%s" % (os.path.dirname(os.path.realpath(__file__)), 'rawes'))

import rawes
from rawes.elastic_exception import ElasticException
import requests


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


def hit_to_metric(hit):
    tags = {}
    for tag in hit['_source']['tags']:
        (k, v) = tag.split('=')
        tags[str(k)] = str(v)
    return {
        'id': hit['_id'],
        'tags': tags
    }


class PluginError(Exception):

    def __init__(self, plugin, msg, underlying_error):
        self.plugin = plugin
        self.msg = msg
        self.underlying_error = underlying_error

    def __str__(self):
        return "%s -> %s (%s)" % (self.plugin, self.msg, self.underlying_error)


class StructuredMetrics(object):

    def __init__(self, config, logger=logging):
        self.plugins = []
        self.es = rawes.Elastic("%s:%s" % (config.es_host, config.es_port))
        self.logger = logger

    def load_plugins(self):
        '''
        loads all the plugins sub-modules
        returns encountered errors, doesn't raise them because
        whoever calls this function defines how any errors are
        handled. meanwhile, loading must continue
        '''
        from plugins import Plugin
        import plugins
        errors = []
        plugins_dir = os.path.dirname(plugins.__file__)
        wd = os.getcwd()
        os.chdir(plugins_dir)
        for f in os.listdir("."):
            if f == '__init__.py' or not f.endswith(".py"):
                continue
            module = f[:-3]
            try:
                imp = __import__('plugins.' + module, globals(), locals(), ['*'])
            except Exception, e:
                errors.append(PluginError(module, "Failed to add plugin '%s'" % module, e))
                continue

            for itemname in dir(imp):
                item = getattr(imp, itemname)
                if isclass(item) and item != Plugin and issubclass(item, Plugin):
                    try:
                        self.plugins.append((module, item()))
                    # regex error is too vague to stand on its own
                    except sre_constants.error, e:
                        e = "error problem parsing matching regex: %s" % e
                        errors.append(PluginError(module, "Failed to add plugin '%s'" % module, e))
                    except Exception, e:
                        errors.append(PluginError(module, "Failed to add plugin '%s'" % module, e))
        os.chdir(wd)
        # sort plugins by their matching priority
        self.plugins = sorted(self.plugins, key=lambda t: t[1].priority, reverse=True)
        return errors

    def list_metrics(self, metrics):
        for plugin in self.plugins:
            (plugin_name, plugin_object) = plugin
            plugin_object.reset_target_yield_counters()
        targets = {}
        plugin_stats = {}
        for plugin in self.plugins:
            plugin_stats[plugin[0]] = 0
        for metric in metrics:
            for (i, plugin) in enumerate(self.plugins):
                (plugin_name, plugin_object) = plugin
                proto2_metric = plugin_object.upgrade_metric(metric)
                if proto2_metric is not None:
                    (k, v) = proto2_metric
                    tags = v['tags']
                    if 'target_type' not in tags or ('unit' not in tags and 'what' not in tags):
                        self.logger.warn("metric '%s' doesn't have the mandatory tags. ('target_type' and either 'unit' or 'what').  ignoring it...", v)
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
        self.es.post('graphite_metrics/metric/_bulk', data=body)

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
            self.es.post('graphite_metrics', data=body)
        except ElasticException as e:
            if e.result['error'] == 'IndexAlreadyExistsException[[graphite_metrics] Already exists]':
                pass
            else:
                raise
        self.logger.debug("making sure shard is started..")
        while True:
            index = self.es.get('graphite_metrics/_status')
            shard = index['indices']['graphite_metrics']['shards']['0'][0]
            self.logger.debug("shard[0][0] state: %s" % shard['state'])
            if shard['state'] == 'STARTED':
                break
            time.sleep(0.1)

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
        ret = self.es.post('graphite_metrics/metric/_count')
        return ret['count']

    def build_es_query(self, query):
        conditions = []
        for (k, data) in query.items():
            negate = data['negate']
            if 'match_tag_equality' in data:
                data = data['match_tag_equality']
                if data[0] and data[1]:
                    condition = es_query('match', 'tags', "%s=%s" % tuple(data))
                elif data[0]:
                    condition = es_regexp('tags', "%s=.*" % data[0])  # i think a '^' prefix is implied here
                elif data[1]:
                    condition = es_regexp('tags', ".*=%s$" % data[0])
            elif 'match_tag_regex' in data:
                data = data['match_tag_regex']
                if data[0] and data[1]:
                    condition = es_regexp('tags', '%s=.*%s.*' % tuple(data))  # i think a '^' prefix is implied here
                elif data[0]:
                    condition = es_regexp('tags', '.*%s.*=.*' % data[0])
                elif data[1]:
                    condition = es_regexp('tags', '.*=.*%s.*' % data[1])
            elif 'match_id_regex' in data:
                # here 'id' is to be interpreted loosely, as in the old
                # (python-native datastructures) approach where we used
                # Plugin.get_target_id to have an id that contains the graphite
                # metric, but also the tags etc. so if the user types just a
                # word, we want the metrics to be returned where the id or tags
                # are matched
                condition = {
                    "or": [
                        es_regexp('_id', '.*%s.*' % k),
                        es_regexp('tags', '.*%s.*' % k)
                    ]
                }
            if negate:
                condition = {"not": condition}
            conditions.append(condition)
        return {
            "filtered": {
                "query": {"match_all": {}},
                "filter": {
                    "and": conditions
                }
            }
        }

    def get_metrics(self, query=None, size=1000):
        self.assure_index()
        try:
            if query is None:
                query = query_all
            return self.es.get('graphite_metrics/metric/_search?size=%s' % size, data={
                "query": query,
            })
        except requests.exceptions.ConnectionError as e:
            sys.stderr.write("Could not connect to ElasticSearch: %s" % e)

    def get_all_metrics(self, query=None, size=200):
        self.assure_index()
        try:
            if query is None:
                query = query_all
            d = self.es.get('graphite_metrics/metric/_search?search_type=scan&scroll=10m&size=%s' % size, data={
                "query": query,
            })
            scroll_id = d['_scroll_id']
            d = None
            while (d is None or len(d['hits']['hits'])):
                d = self.es.get('_search/scroll?scroll=10m', data=scroll_id)
                yield d
                scroll_id = d['_scroll_id']
        except requests.exceptions.ConnectionError as e:
            sys.stderr.write("Could not connect to ElasticSearch: %s" % e)

    def get(self, metric_id):
        self.assure_index()
        return self.es.get('graphite_metrics/metric/%s' % metric_id)

    def matching(self, patterns):
        self.assure_index()
        # future optimisation: query['limit_targets'] can be applied if no
        # sum_by or kind of later aggregation
        es_query = self.build_es_query(patterns)
        metrics = self.get_metrics(es_query)
        results = {}
        for hit in metrics['hits']['hits']:
            metric = hit_to_metric(hit)
            results[metric['id']] = metric
        return results
