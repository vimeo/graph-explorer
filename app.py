#!/usr/bin/env python2
from bottle import route, template, request, static_file, redirect, response, default_app
import config
import preferences
from urlparse import urljoin
import structured_metrics
from graphs import Graphs
from backend import Backend, get_action_on_rules_match
from simple_match import match
from query import parse_query, normalize_query, parse_patterns
from target import Target
import logging
import re
import convert


# contains all errors as key:(title,msg) items.
# will be used throughout the runtime to track all encountered errors
errors = {}

# will contain the latest data
last_update = None

logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)
chandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
chandler.setFormatter(formatter)
logger.addHandler(chandler)
if config.log_file:
    fhandler = logging.FileHandler(config.log_file)
    fhandler.setFormatter(formatter)
    logger.addHandler(fhandler)

logger.debug('app starting')
backend = Backend(config, logger)
s_metrics = structured_metrics.StructuredMetrics(config, logger)
graphs = Graphs()
graphs.load_plugins()
graphs_all = graphs.list_graphs()


@route('<path:re:/assets/.*>')
@route('<path:re:/timeserieswidget/.*js>')
@route('<path:re:/timeserieswidget/.*css>')
@route('<path:re:/timeserieswidget/timezone-js/src/.*js>')
@route('<path:re:/timeserieswidget/tz/.*>')
@route('<path:re:/DataTables/media/js/.*js>')
@route('<path:re:/DataTablesPlugins/integration/bootstrap/.*js>')
@route('<path:re:/DataTablesPlugins/integration/bootstrap/.*css>')
def static(path):
    return static_file(path, root='.')


@route('/', method='GET')
@route('/index', method='GET')
@route('/index/', method='GET')
@route('/index/<query:path>', method='GET')
def index(query=''):
    from suggested_queries import suggested_queries
    body = template('templates/body.index', errors=errors, query=query, suggested_queries=suggested_queries)
    return render_page(body)


@route('/dashboard/<dashboard_name>')
def slash_dashboard(dashboard_name=None):
    dashboard = template('templates/dashboards/%s' % dashboard_name, errors=errors)
    return render_page(dashboard)


def render_page(body, page='index'):
    return unicode(template('templates/page', body=body, page=page, last_update=last_update))


@route('/meta')
def meta():
    body = template('templates/body.meta', todo=template('templates/' + 'todo'.upper()))
    return render_page(body, 'meta')


# accepts comma separated list of metric_id's
@route('/inspect/<metrics>')
def inspect_metric(metrics=''):
    metrics = map(s_metrics.load_metric, metrics.split(','))
    args = {'errors': errors,
            'metrics': metrics,
            'config': config
            }
    body = template('templates/body.inspect', args)
    return render_page(body, 'inspect')


def build_graphs(graphs, query={}):
    defaults = {
        'from': '-24hours',
        'to': 'now'
    }
    query = dict(defaults.items() + query.items())
    query['until'] = query['to']
    del query['to']
    for (k, v) in graphs.items():
        v.update(query)
    return graphs


def graphs_limit_targets(nolimit_graphs, limit):
    targets_used = 0
    limit_graphs = {}
    for (graph_key, graph_config) in nolimit_graphs.items():
        limit_graphs[graph_key] = graph_config
        nolimit_targets = graph_config['targets']
        limit_graphs[graph_key]['targets'] = []
        for target in nolimit_targets:
            targets_used += 1
            limit_graphs[graph_key]['targets'].append(target)
            if targets_used == limit:
                return limit_graphs
    return limit_graphs


def graphite_func_aggregate(targets, agg_by_tags, aggfunc):
    # differentiators is a list of tag values that set the contributing targets apart
    # this will be used later in the UI
    differentiators = {}
    for t in targets:
        for agg_by_tag in agg_by_tags.keys():
            differentiators[agg_by_tag] = differentiators.get(agg_by_tag, [])
            differentiators[agg_by_tag].append(t['variables'][agg_by_tag])
    t = {
        'target': '%s(%s)' % (aggfunc, ','.join([t['target'] for t in targets])),
        'id': [t['id'] for t in targets],
        'variables': targets[0]['variables']
    }
    bucket_id = targets[0]['match_buckets'][agg_by_tag]
    bucket_id_str = ''
    if bucket_id:
        bucket_id_str = "'%s' " % bucket_id
    for agg_by_tag in agg_by_tags:
        t['variables'][agg_by_tag] = ('%s%s (%s values)' % (bucket_id_str, aggfunc, len(targets)), differentiators[agg_by_tag])
    return Target(t)


def build_graphs_from_targets(targets, query={}, target_modifiers=[]):
    # merge default options..
    defaults = {
        'group_by': [],
        'sum_by': {},
        'avg_over': None,
        'avg_by': {},
        'from': '-24hours',
        'to': 'now',
        'statement': 'graph',
        'limit_targets': 500
    }
    query = dict(defaults.items() + query.items())
    graphs = {}
    if not targets:
        return (graphs, query)
    group_by = query['group_by']
    sum_by = query['sum_by']
    avg_by = query['avg_by']
    avg_over = query['avg_over']
    # i'm gonna assume you never use second and your datapoints are stored with
    # minutely resolution. later on we can use config options for this (or
    # better: somehow query graphite about it)
    # note, the day/week/month numbers are not technically accurate, but
    # since we're doing movingAvg that's ok
    averaging = {
        'M': 1,
        'h': 60,
        'd': 60 * 24,
        'w': 60 * 24 * 7,
        'mo': 60 * 24 * 30
    }
    if avg_over is not None:
        avg_over_amount = avg_over[0]
        avg_over_unit = avg_over[1]
        if avg_over_unit in averaging.keys():
            multiplier = averaging[avg_over_unit]
            target_modifier = {'target': ['movingAverage', str(avg_over_amount * multiplier)]}
            target_modifiers.append(target_modifier)

    # for each combination of values of tags from group_by, make 1 graph with
    # all targets that have these values. so for each graph, we have:
    # the "constants": tags in the group_by
    # the "variables": tags not in the group_by, which can have arbitrary values
    # go through all targets and group them into graphs:
    for (i, target_id) in enumerate(sorted(targets.iterkeys())):
        constants = {}
        variables = {}
        target_data = targets[target_id]
        for (tag_name, tag_value) in target_data['tags'].items():
            if tag_name in group_by or '%s=' % tag_name in group_by:
                constants[tag_name] = tag_value
            else:
                variables[tag_name] = tag_value
        graph_key = '__'.join([target_data['tags'][tag_name] for tag_name in constants])
        if graph_key not in graphs:
            graph = {'from': query['from'], 'until': query['to']}
            graph.update({'constants': constants, 'targets': []})
            graphs[graph_key] = graph
        # set all options needed for timeserieswidget/flot:
        t = {
            'variables': variables,
            'id': target_data['id'],  # timeserieswidget doesn't care about this
            'target': target_data['id']
        }
        if 'color' in target_data:
            t['color'] = target_data['color']
        graphs[graph_key]['targets'].append(Target(t))

    # ok so now we have a graphs dictionary with a graph for every approriate
    # combination of group_by tags, and each graphs contains all targets that
    # should be shown on it.  but the user may have asked to aggregate certain
    # targets together, by summing and/or averaging across different values of
    # (a) certain tag(s). let's process the aggregations now.
    if (sum_by or avg_by):
        for (graph_key, graph_config) in graphs.items():
            graph_config['targets_sum_candidates'] = {}
            graph_config['targets_avg_candidates'] = {}
            graph_config['normal_targets'] = []

            for target in graph_config['targets']:
                sum_id = target.get_agg_key(sum_by)
                if sum_id:
                    if sum_id not in graph_config['targets_sum_candidates']:
                        graphs[graph_key]['targets_sum_candidates'][sum_id] = []
                    graph_config['targets_sum_candidates'][sum_id].append(target)

            for (sum_id, targets) in graph_config['targets_sum_candidates'].items():
                if len(targets) > 1:
                    for t in targets:
                        graph_config['targets'].remove(t)
                    graph_config['targets'].append(
                        graphite_func_aggregate(targets, sum_by, "sumSeries"))

            for target in graph_config['targets']:
                # Now that any summing is done, we look at aggregating by
                # averaging because avg(foo+bar+baz) is more efficient
                # than avg(foo)+avg(bar)+avg(baz)
                # aggregate targets (whether those are sums or regular ones)
                avg_id = target.get_agg_key(avg_by)
                if avg_id:
                    if avg_id not in graph_config['targets_avg_candidates']:
                        graph_config['targets_avg_candidates'][avg_id] = []
                    graph_config['targets_avg_candidates'][avg_id].append(target)

            for (avg_id, targets) in graph_config['targets_avg_candidates'].items():
                if len(targets) > 1:
                    for t in targets:
                        graph_config['targets'].remove(t)
                    graph_config['targets'].append(
                        graphite_func_aggregate(targets, avg_by, "averageSeries"))

    # remove targets/graphs over the limit
    graphs = graphs_limit_targets(graphs, query['limit_targets'])

    # Apply target modifiers (like movingAverage, summarize, ...)
    for (graph_key, graph_config) in graphs.items():
        for target in graph_config['targets']:
            for target_modifier in target_modifiers:
                target['target'] = "%s(%s,%s)" % (target_modifier['target'][0],
                                                  target['target'],
                                                  ','.join(target_modifier['target'][1:]))
                if 'tags' in target_modifier:
                    for (new_k, new_v) in target_modifier['tags'].items():
                        if new_k in graph_config['constants']:
                            graph_config['constants'][new_k] = new_v
                        else:
                            target['variables'][new_k] = new_v
    # if in a graph all targets have a tag with the same value, they are
    # effectively constants, so promote them.  this makes the display of the
    # graphs less rendundant and makes it easier to do config/preferences
    # on a per-graph basis.
    for (graph_key, graph_config) in graphs.items():
        # get all variable tags throughout all targets in this graph
        tags_seen = set()
        for target in graph_config['targets']:
            for tag_name in target['variables'].keys():
                tags_seen.add(tag_name)

        # find effective constants from those variables,
        # and effective variables. (unset tag is a value too)
        first_values_seen = {}
        effective_variables = set()  # tags for which we've seen >1 values
        for target in graph_config['targets']:
            for tag_name in tags_seen:
                # already known that we can't promote, continue
                if tag_name in effective_variables:
                    continue
                tag_value = target['variables'].get(tag_name, None)
                if tag_name not in first_values_seen:
                    first_values_seen[tag_name] = tag_value
                elif tag_value != first_values_seen[tag_name]:
                    effective_variables.add(tag_name)
        effective_constants = tags_seen - effective_variables

        # promote the effective_constants by adjusting graph and targets:
        graphs[graph_key]['promoted_constants'] = {}
        for tag_name in effective_constants:
            graphs[graph_key]['promoted_constants'][tag_name] = first_values_seen[tag_name]
            for (i, target) in enumerate(graph_config['targets']):
                if tag_name in graphs[graph_key]['targets'][i]['variables']:
                    del graphs[graph_key]['targets'][i]['variables'][tag_name]

        # now that graph config is "rich", merge in settings from preferences
        constants = dict(graphs[graph_key]['constants'].items() + graphs[graph_key]['promoted_constants'].items())
        for graph_option in get_action_on_rules_match(preferences.graph_options, constants):
            if isinstance(graph_option, dict):
                graphs[graph_key].update(graph_option)
            else:
                graphs[graph_key] = graph_option(graphs[graph_key])

        # but, the query may override some preferences:
        override = {}
        if query['statement'] == 'lines':
            override['state'] = 'lines'
        if query['statement'] == 'stack':
            override['state'] = 'stacked'
        if query['min'] is not None:
            override['yaxis'] = override.get('yaxis', {})
            override['yaxis'].update({'min': convert.parse_str(query['min'])})
        if query['max'] is not None:
            override['yaxis'] = override.get('yaxis', {})
            override['yaxis'].update({'max': convert.parse_str(query['max'])})

        graphs[graph_key].update(override)

    # now that some constants are promoted, we can give the graph more
    # unique keys based on all (original + promoted) constants. this is in
    # line with the meaning of the graph ("all targets with those constant
    # tags"), but more importantly: this fixes cases where some graphs
    # would otherwise have the same key, even though they have a different
    # set of constants, this can manifest itself on dashboard pages where
    # graphs for different queries are shown.
    new_graphs = {}
    for (graph_key, graph_config) in graphs.items():
        better_graph_key_1 = '__'.join('%s_%s' % i for i in graph_config['constants'].items())
        better_graph_key_2 = '__'.join('%s_%s' % i for i in graph_config['promoted_constants'].items())
        better_graph_key = '%s___%s' % (better_graph_key_1, better_graph_key_2)
        new_graphs[better_graph_key] = graph_config
    graphs = new_graphs

    return (graphs, query)


@route('/graphs/', method='POST')
@route('/graphs/<query:path>', method='GET')  # used for manually testing
def graphs(query=''):
    return handle_graphs(query, False)


@route('/graphs_deps/', method='POST')
@route('/graphs_deps/<query:path>', method='GET')  # used for manually testing
def graphs_deps(query=''):
    return handle_graphs(query, True)


def handle_graphs(query, deps):
    '''
    get all relevant graphs matching query,
    graphs from structured_metrics targets, as well as graphs
    defined in structured_metrics plugins
    '''
    if 'metrics_file' in errors:
        return template('templates/graphs', errors=errors)
    if not query:
        query = request.forms.get('query')
    if not query:
        return template('templates/graphs', query=query, errors=errors)

    return render_graphs(query, deps=deps)


@route('/render/<query>')
@route('/render/', method='POST')
@route('/render', method='POST')
def proxy_render(query=''):
    import sys
    import urllib2
    url = urljoin(config.graphite_url, "/render/" + query)
    body = request.body.read()
    f = urllib2.urlopen(url, body)
    # this can be very verbose:
    #logger.debug("proxying graphite request: " + body)
    message = f.info()
    response.headers['Content-Type'] = message.gettype()
    return f.read()

@route('/graphs_minimal/<query:path>', method='GET')
def graphs_minimal(query=''):
    return handle_graphs_minimal(query, False)


@route('/graphs_minimal_deps/<query:path>', method='GET')
def graphs_minimal_deps(query=''):
    return handle_graphs_minimal(query, True)


def handle_graphs_minimal(query, deps):
    '''
    like graphs(), but without extra decoration, so can be used on dashboards
    TODO dashboard should show any errors
    '''
    if not query:
        return template('templates/graphs', query=query, errors=errors)
    return render_graphs(query, minimal=True, deps=deps)


def render_graphs(query, minimal=False, deps=False):
    if "query_parse" in errors:
        del errors["query_parse"]
    try:
        query = parse_query(query)
    except Exception, e:
        errors["query_parse"] = ("Couldn't parse query", e)
    if errors:
        body = template('templates/snippet.errors', errors=errors)
        return render_page(body)

    (query, target_modifiers) = normalize_query(query)
    try:
        patterns = parse_patterns(query)
    except Exception, e:
        errors["query_parse"] = ("Couldn't parse query patterns", e)
    if errors:
        body = template('templates/snippet.errors', errors=errors)
        return render_page(body)
    tags = set()
    targets_matching = s_metrics.matching(patterns)
    for target in targets_matching.values():
        for tag_name in target['tags'].keys():
            tags.add(tag_name)
    graphs_matching = match(graphs_all, patterns, True)
    graphs_matching = build_graphs(graphs_matching, query)
    stats = {'len_targets_all': s_metrics.count_metrics(),
             'len_graphs_all': len(graphs_all),
             'len_targets_matching': len(targets_matching),
             'len_graphs_matching': len(graphs_matching),
             }
    out = ''
    graphs = []
    targets_list = {}
    # the code to handle different statements, and the view
    # templates could be a bit prettier, but for now it'll do.
    if query['statement'] in ('graph', 'lines', 'stack'):
        graphs_targets_matching = build_graphs_from_targets(targets_matching, query, target_modifiers)[0]
        stats['len_graphs_targets_matching'] = len(graphs_targets_matching)
        graphs_matching.update(graphs_targets_matching)
        stats['len_graphs_matching_all'] = len(graphs_matching)
        if len(graphs_matching) > 0 and deps:
            out += template('templates/snippet.graph-deps')
        for key in sorted(graphs_matching.iterkeys()):
            graphs.append((key, graphs_matching[key]))
    elif query['statement'] == 'list':
        # for now, only supports targets, not graphs
        targets_list = targets_matching
        stats['len_graphs_targets_matching'] = 0
        stats['len_graphs_matching_all'] = 0

    args = {'errors': errors,
            'query': query,
            'config': config,
            'graphs': graphs,
            'targets_list': targets_list,
            'tags': tags,
            'preferences': preferences
            }
    args.update(stats)
    if minimal:
        out += template('templates/graphs_minimal', args)
    else:
        out += template('templates/graphs', args)
    return out


# vim: ts=4 et sw=4:
