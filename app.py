#!/usr/bin/env python2
import os
import json
import re
from inspect import isclass
from bottle import route, template, request, static_file, redirect, response
import config
import sre_constants

# contains all errors as key:(title,msg) items.
# will be used throughout the runtime to track all encountered errors
errors = {}

# Load all the graph_templates sub-modules and create a list of
# template_objects and templates
from graph_templates import GraphTemplate
import graph_templates
template_objects = []
templates = []
templates_dir = os.path.dirname(graph_templates.__file__)
wd = os.getcwd()
os.chdir(templates_dir)
for f in os.listdir("."):
    if f == '__init__.py' or not f.endswith(".py"):
        continue
    module = f[:-3]
    try:
        imp = __import__('graph_templates.' + module, globals(), locals(), ['*'])
    except Exception, e:
        errors['template_%s' % module] = (
                "Failed to add template '%s'" % module,
                e
        )
        continue

    for itemname in dir(imp):
        item = getattr(imp, itemname)
        if isclass(item) and item != GraphTemplate and issubclass(item, GraphTemplate):
            try:
                template_objects.append(item())
                templates.append(module)
            # regex error is too vague to stand on its own
            except sre_constants.error, e:
                errors['template_%s' % module] = (
                        "Failed to add template '%s'" % module,
                        "error problem parsing matching regex: %s" % e
                )
            except Exception, e:
                errors['template_%s' % module] = (
                        "Failed to add template '%s'" % module,
                        e
                )
os.chdir(wd)


def list_target_types():
    target_types = {}
    default = {
        'default_group_by': None
    }
    for t_o in template_objects:
        for k, v in t_o.target_types.items():
            id = '%s_%s' % (t_o.classname_to_tag(), k)
            target_types[id] = default.copy()
            target_types[id].update(v)
    return target_types


def list_targets(metrics):
    targets = {}
    for t_o in template_objects:
        targets.update(t_o.list_targets(metrics))
    return targets


def list_graphs(metrics):
    graphs = {}
    for t_o in template_objects:
        graphs.update(t_o.list_graphs(metrics))
    return graphs


def parse_query(query_str):
    query = {
        'patterns': [],
        'group_by': ['target_type']
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

    # if user doesn't specify any group_by, we automatically group by target_type and
    # by the tag specified by default_group_by in the target_type, if any.
    # if the user specified "group by foobar" in the query_str, we group by target_type and whatever the user said.
    (query_str, group_by) = parse_out_value(query_str, 'group by ', '[^ ]+', 'default_group_by')
    if group_by != 'default_group_by':
        query['patterns'].append('%s:' % group_by)
    query['group_by'].append(group_by)
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
def match(objects, query):
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
            patterns[pattern]['match_tag_equality'] = pattern.split('=')
        if ':' in pattern:
            patterns[pattern]['match_tag_regex'] = pattern.split(':')
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
@route('<path:re:/graphitejs/.*js>')
@route('<path:re:/graphitejs/.*css>')
def static(path):
    return static_file(path, root='.')


@route('/', method='GET')
@route('/index', method='GET')
@route('/index/', method='GET')
@route('/index/<query>', method='GET')
def index(query=''):
    from suggested_queries import suggested_queries
    body = template('body.index', errors=errors, query=query, suggested_queries=suggested_queries)
    return render_page(body)


def render_page(body, page='index'):
    try:
        stat = stat_metrics()
        e = None
    except OSError, e:
        stat = None
    return str(template('page', body=body, page=page, stat_metrics=stat, stat_metrics_error=e))


@route('/index', method='POST')
def index_post():
    redirect('/index/%s' % request.forms.query)


@route('/meta')
def meta():
    body = template('body.meta', todo=template('todo'.upper()))
    return render_page(body, 'meta')


@route('/debug')
def view_debug():
    try:
        metrics = load_metrics()
    except IOError, e:
        errors['metrics_file'] = ("Can't load metrics file", e)
        body = template('snippet.errors', errors=errors)
        return render_page(body, 'debug')
    except ValueError, e:
        errors['metrics_file'] = ("Can't parse metrics file", e)
        body = template('snippet.errors', errors=errors)
        return render_page(body, 'debug')
    target_types = list_target_types()
    targets = list_targets(metrics)
    graphs = list_graphs(metrics)
    graphs_targets, graphs_targets_options = build_graphs_from_targets(target_types, targets)
    args = {'errors': errors,
            'templates': templates,
            'targets': targets,
            'graphs': graphs,
            'graphs_targets': graphs_targets,
            'graphs_targets_options': graphs_targets_options
            }
    body = template('body.debug', args)
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


def build_graphs_from_targets(target_types, targets, query={}):
    # merge default options..
    defaults = {
        'group_by': ['target_type', 'default_group_by'],
        'from': '-24hours',
        'to': 'now'
    }
    query = dict(defaults.items() + query.items())
    graphs = {}
    if not targets:
        return (graphs, query)
    group_by = query['group_by']
    # for each combination of elements specified by group_by, make 1 graph,
    # containing all various targets that have the elements specified by group_by
    # graph name: value of each name of the elements specified by group_by (the "constants" for this graph)
    # alias names: values of each name of the elements *not* specified by group_by (the "variables" for this graph)
    # currently we support these group_by lists:
    # target_type <tag>
    # target_type <default_group_by (which also resolves to a tag)>
    # go through all targets, figure out the corresponding graph title and target title and data, and categorize them into graphs
    constants = len(group_by)
    for target_id in sorted(targets.iterkeys()):
        target_data = targets[target_id]
        target_type = '%s_%s' % (target_data['tags']['template'], target_data['tags']['target_type'])
        constants = ['targets', target_type]
        if group_by[1] is 'default_group_by':
            group_by_tag = target_types[target_type]['default_group_by']
        else:
            group_by_tag = group_by[1]
        # group_by_tag is now something like 'server' or 'type' or None, convert it to the actual value:
        if group_by_tag is not None:
            group_by_tag = target_data['tags'][group_by_tag]
            constants.append(group_by_tag)
        variables = []
        for tag_id in sorted(target_data['tags'].iterkeys()):
            tag_value = target_data['tags'][tag_id]
            if tag_value not in constants and tag_value:
                variables.append(tag_value)

        graph_title = ' '.join(constants)
        target_name = ' '.join(variables)
        if graph_title not in graphs:
            graph = {'from': query['from'], 'until': query['to']}
            graph.update(target_types[target_type].get('default_graph_options', {}))
            graph.update({'title': graph_title, 'targets': []})
            graphs[graph_title] = graph
        # set all options needed for graphitejs/flot:
        t = {
            'name': target_name,
            'target': target_data['target']
        }
        if 'color' in target_data:
            t['color'] = target_data['color']
        graphs[graph_title]['targets'].append(t)
    # given all graphs, process them to set any further options
    # nothing needed at this point.
    return (graphs, query)


@route('/graphs/', method='POST')
@route('/graphs/<query>', method='GET')  # used for manually testing
def graphs(query=''):
    '''
    get all relevant graphs matching query,
    graphs yielded by templates directly,
    enriched by combining the yielded targets
    '''
    try:
        metrics = load_metrics()
    except IOError, e:
        errors['metrics_file'] = ("Can't load metrics file", e)
        return template('graphs', errors=errors)
    except ValueError, e:
        errors['metrics_file'] = ("Can't parse metrics file", e)
        return template('graphs', errors=errors)
    if not query:
        query = request.forms.get('query')
    if not query:
        return template('graphs', query=query, errors=errors)
    target_types = list_target_types()
    targets_all = list_targets(metrics)
    graphs_all = list_graphs(metrics)
    query = parse_query(query)
    targets_matching = match(targets_all, query)
    graphs_matching = match(graphs_all, query)
    graphs_targets_matching = build_graphs_from_targets(target_types, targets_matching, query)[0]
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
        out += template('snippet.graph-deps')

    rendered_templates = []
    for title in sorted(graphs_matching.iterkeys()):
        data = graphs_matching[title]
        rendered_templates.append(template('snippet.graph', config=config, graph_name=title, graph_data=data))
    args = {'errors': errors,
            'query': query,
    }
    args.update(stats)
    return template('graphs', args) + ''.join(rendered_templates)

# vim: ts=4 et sw=4:
