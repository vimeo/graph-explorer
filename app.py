#!/usr/bin/env python2
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        raise ImportError("GE requires python2, 2.6 or higher, or 2.5 with simplejson.")
import os
import re
from inspect import isclass
from bottle import route, template, request, static_file, redirect, response
import config
import preferences
import sre_constants

# contains all errors as key:(title,msg) items.
# will be used throughout the runtime to track all encountered errors
errors = {}

# Load all the plugins sub-modules and create a list of
# plugin_objects and plugin_names
from plugins import Plugin
import plugins
plugin_objects = []
plugin_names = []
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
        errors['plugin_%s' % module] = (
            "Failed to add plugin '%s'" % module,
            e
        )
        continue

    for itemname in dir(imp):
        item = getattr(imp, itemname)
        if isclass(item) and item != Plugin and issubclass(item, Plugin):
            try:
                plugin_objects.append(item())
                plugin_names.append(module)
            # regex error is too vague to stand on its own
            except sre_constants.error, e:
                errors['plugin_%s' % module] = (
                    "Failed to add plugin '%s'" % module,
                    "error problem parsing matching regex: %s" % e
                )
            except Exception, e:
                errors['plugin_%s' % module] = (
                    "Failed to add plugin '%s'" % module,
                    e
                )
os.chdir(wd)


def list_targets(metrics):
    targets = {}
    for t_o in plugin_objects:
        targets.update(t_o.list_targets(metrics))
    return targets


def list_graphs(metrics):
    graphs = {}
    for t_o in plugin_objects:
        graphs.update(t_o.list_graphs(metrics))
    return graphs


def parse_query(query_str):
    query = {
        'patterns': [],
        'group_by': ['target_type=', 'what=', 'server']
    }

    # for a call like ('foo bar baz quux', 'bar ', 'baz', 'def')
    # returns ('foo quux', 'baz') or the original query and the default val if no match
    def parse_out_value(query_str, predicate_match, value_match, value_default):
        match = re.search('(%s%s)' % (predicate_match, value_match), query_str)
        value = value_default
        if match and match.groups() > 0:
            value = match.groups(1)[0].replace(predicate_match, '')
            query_str = query_str[:match.start(1)] + query_str[match.end(1):]
        return (query_str, value)

    (query_str, query['to']) = parse_out_value(query_str, 'to ', '[^ ]+', 'now')
    (query_str, query['from']) = parse_out_value(query_str, 'from ', '[^ ]+', '-24hours')

    (query_str, group_by_str) = parse_out_value(query_str, 'GROUP BY ', '[^ ]+', None)
    (query_str, extra_group_by_str) = parse_out_value(query_str, 'group by ', '[^ ]+', None)
    if group_by_str is not None:
        query['group_by'] = group_by_str.split(',')
    elif extra_group_by_str is not None:
        query['group_by'] = [tag for tag in query['group_by'] if tag.endswith('=')]
        query['group_by'].extend(extra_group_by_str.split(','))
    for tag in query['group_by']:
        if tag.endswith('='):
            query['patterns'].append(tag)

    # split query_str into multiple patterns which are all matched independently
    # this allows you write patterns in any order, and also makes it easy to use negations
    query['patterns'] += query_str.split()
    return query


# id, data -> an key:object from the dict of objects
# pattern: a pattern structure from match()
def match_pattern(id, data, pattern):
    if 'match_tag_equality' in pattern:
        t_key = pattern['match_tag_equality'][0]
        t_val = pattern['match_tag_equality'][1]
        if len(t_key) is 0 and len(t_val) is 0:
            # this pattern is pointless.
            match_pattern = True
        if len(t_key) > 0 and len(t_val) is 0:
            match_pattern = (t_key in data['tags'])
        if len(t_key) is 0 and len(t_val) > 0:
            match_pattern = False
            for v in data['tags'].values():
                if t_val is v:
                    match_pattern = True
                    break
        if len(t_key) > 0 and len(t_val) > 0:
            match_pattern = (t_key in data['tags'] and data['tags'][t_key] == t_val)
    elif 'match_tag_regex' in pattern:
        t_key = pattern['match_tag_regex'][0]
        t_val = pattern['match_tag_regex'][1]
        if len(t_key) is 0 and len(t_val) is 0:
            # this pattern is pointless.
            match_pattern = True
        if len(t_key) > 0 and len(t_val) is 0:
            match_pattern = False
            for k in data['tags'].iterkeys():
                if re.search(t_key, k) is not None:
                    match_pattern = True
                    break
        if len(t_key) is 0 and len(t_val) > 0:
            match_pattern = False
            for v in data['tags'].values():
                if re.search(t_val, v) is not None:
                    match_pattern = True
                    break
        if len(t_key) > 0 and len(t_val) > 0:
            match_pattern = (t_key in data['tags'] and re.search(t_val, data['tags'][t_key]) is not None)
    else:
        match_pattern = (pattern['match_id_regex'].search(id) is not None)
    return match_pattern


# objects is expected to be a dict with elements like id: data
# id's are matched, and the return value is a dict in the same format
# if you use tags, make sure data['tags'] is a dict of tags or this'll blow up
# if graph, ignores patterns that only apply for targets (tag matching on target_type, what)
def match(objects, query, graph=False):
    # prepare higher performing query structure
    # note that if you have twice the exact same "word" (ignoring leading '!'), the last one wins
    patterns = {}
    for pattern in query['patterns']:
        negate = False
        if pattern.startswith('!'):
            negate = True
            pattern = pattern[1:]
        patterns[pattern] = {'negate': negate}
        if '=' in pattern:
            if not graph or pattern not in ('target_type=', 'what='):
                patterns[pattern]['match_tag_equality'] = pattern.split('=')
            else:
                del patterns[pattern]
        elif ':' in pattern:
            if not graph or pattern not in ('target_type:', 'what:'):
                patterns[pattern]['match_tag_regex'] = pattern.split(':')
            else:
                del patterns[pattern]
        else:
            patterns[pattern]['match_id_regex'] = re.compile(pattern)

    objects_matching = {}
    for (id, data) in objects.items():
        match_o = True
        for pattern in patterns.values():
            match_p = match_pattern(id, data, pattern)
            if match_p and pattern['negate']:
                match_o = False
            elif not match_p and not pattern['negate']:
                match_o = False
        if match_o:
            objects_matching[id] = data
    return objects_matching


def load_metrics():
    f = open('metrics.json', 'r')
    return json.load(f)


def stat_metrics():
    return os.stat('metrics.json')


@route('<path:re:/assets/.*>')
@route('<path:re:/timeserieswidget/.*js>')
@route('<path:re:/timeserieswidget/.*css>')
@route('<path:re:/DataTables/media/js/.*js>')
@route('<path:re:/DataTablesPlugins/integration/bootstrap/.*js>')
@route('<path:re:/DataTablesPlugins/integration/bootstrap/.*css>')
def static(path):
    return static_file(path, root='.')


@route('/', method='GET')
@route('/index', method='GET')
@route('/index/', method='GET')
@route('/index/<query>', method='GET')
def index(query=''):
    from suggested_queries import suggested_queries
    body = template('templates/body.index', errors=errors, query=query, suggested_queries=suggested_queries)
    return render_page(body)


def render_page(body, page='index'):
    try:
        stat = stat_metrics()
        e = None
    except OSError, e:
        stat = None
    return str(template('templates/page', body=body, page=page, stat_metrics=stat, stat_metrics_error=e))


@route('/index', method='POST')
def index_post():
    redirect('/index/%s' % request.forms.query)


@route('/meta')
def meta():
    body = template('templates/body.meta', todo=template('templates/' + 'todo'.upper()))
    return render_page(body, 'meta')


@route('/inspect/<metric>')
def inspect_metric(metric=''):
    metrics = [metric]
    targets = list_targets(metrics)
    args = {'errors': errors,
            'plugin_names': plugin_names,
            'targets': targets,
            }
    body = template('templates/body.inspect', args)
    return render_page(body, 'inspect')


@route('/debug')
@route('/debug/<query>')
def view_debug(query=''):
    try:
        metrics = load_metrics()
    except IOError, e:
        errors['metrics_file'] = ("Can't load metrics file", e)
        body = template('templates/snippet.errors', errors=errors)
        return render_page(body, 'debug')
    except ValueError, e:
        errors['metrics_file'] = ("Can't parse metrics file", e)
        body = template('templates/snippet.errors', errors=errors)
        return render_page(body, 'debug')
    targets_all = list_targets(metrics)
    graphs_all = list_graphs(metrics)
    if query:
        query = parse_query(query)
        targets_matching = match(targets_all, query)
        graphs_matching = match(graphs_all, query, True)
        graphs_targets, graphs_targets_options = build_graphs_from_targets(targets_matching, query)
        targets = targets_matching
        graphs = graphs_matching
    else:
        graphs_targets, graphs_targets_options = build_graphs_from_targets(targets_all)
        targets = targets_all
        graphs = graphs_all

    args = {'errors': errors,
            'plugin_names': plugin_names,
            'targets': targets,
            'graphs': graphs,
            'graphs_targets': graphs_targets,
            'graphs_targets_options': graphs_targets_options
            }
    body = template('templates/body.debug', args)
    return render_page(body, 'debug')


@route('/debug/metrics')
def debug_metrics():
    response.content_type = 'text/plain'
    try:
        return "\n".join(load_metrics())
    except IOError, e:
        response.status = 500
        return "Can't load metrics file: %s" % e
    except ValueError, e:
        response.status = 500
        return "Can't parse metrics file: %s" % e


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


def build_graphs_from_targets(targets, query={}):
    # merge default options..
    defaults = {
        'group_by': [],
        'from': '-24hours',
        'to': 'now'
    }
    query = dict(defaults.items() + query.items())
    graphs = {}
    if not targets:
        return (graphs, query)
    group_by = query['group_by']
    # for each combination of values of tags from group_by, make 1 graph with
    # all targets that have these values. so for each graph, we have:
    # the "constants": tags in the group_by
    # the "variables": tags not in the group_by, which can have arbitrary values
    # go through all targets and group them into graphs:
    for target_id in sorted(targets.iterkeys()):
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
            'graphite_metric': target_data['graphite_metric'],
            'target': target_data['target']
        }
        if 'color' in target_data:
            t['color'] = target_data['color']
        graphs[graph_key]['targets'].append(t)
    # if in a graph all targets have a tag with the same value, they are
    # effectively constants, so promote them.  this makes the display of the
    # graphs less rendundant and paves the path
    # for later configuration on a per-graph basis.
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
        for (match_rules, graph_options) in preferences.graph_options:
            rule_match = True
            for (tag_k, tag_v) in match_rules.items():
                if tag_k not in constants:
                    rule_match = False
                    break
                if isinstance(tag_v, basestring):
                    if constants[tag_k] != tag_v:
                        rule_match = False
                        break
                else:
                    # tag_v is a list -> OR of multiple allowed options
                    tag_match = False
                    for option in tag_v:
                        if constants[tag_k] == option:
                            tag_match = True
                    if not tag_match:
                        rule_match = False
                        break
            if rule_match:
                graphs[graph_key].update(graph_options)



    return (graphs, query)


@route('/graphs/', method='POST')
@route('/graphs/<query>', method='GET')  # used for manually testing
def graphs(query=''):
    '''
    get all relevant graphs matching query,
    graphs yielded by plugins directly,
    enriched by combining the yielded targets
    '''
    try:
        metrics = load_metrics()
    except IOError, e:
        errors['metrics_file'] = ("Can't load metrics file", e)
        return template('templates/graphs', errors=errors)
    except ValueError, e:
        errors['metrics_file'] = ("Can't parse metrics file", e)
        return template('templates/graphs', errors=errors)
    if not query:
        query = request.forms.get('query')
    if not query:
        return template('templates/graphs', query=query, errors=errors)
    targets_all = list_targets(metrics)
    graphs_all = list_graphs(metrics)
    query = parse_query(query)
    tags = set()
    targets_matching = match(targets_all, query)
    for target in targets_matching.values():
        for tag_name in target['tags'].keys():
            tags.add(tag_name)
    graphs_matching = match(graphs_all, query, True)
    graphs_matching = build_graphs(graphs_matching, query)
    graphs_targets_matching = build_graphs_from_targets(targets_matching, query)[0]
    stats = {'len_targets_all': len(targets_all),
             'len_graphs_all': len(graphs_all),
             'len_targets_matching': len(targets_matching),
             'len_graphs_matching': len(graphs_matching),
             'len_graphs_targets_matching': len(graphs_targets_matching),
             }
    graphs_matching.update(graphs_targets_matching)
    stats['len_graphs_matching_all'] = len(graphs_matching)
    out = ''
    if len(graphs_matching) > 0 and request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        out += template('templates/snippet.graph-deps')

    graphs = []
    for key in sorted(graphs_matching.iterkeys()):
        graphs.append((key, graphs_matching[key]))

    args = {'errors': errors,
            'query': query,
            'config': config,
            'graphs': graphs,
            'tags': tags,
            'count_interval': preferences.count_interval
            }
    args.update(stats)
    out += template('templates/graphs', args)
    return out

# vim: ts=4 et sw=4:
