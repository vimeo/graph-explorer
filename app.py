#!/usr/bin/env python2
import os, json, sys, traceback, re
from inspect import isclass
from bottle import route, run, debug, template, request, validate, static_file, redirect, response
from config import *

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
    imp = __import__('graph_templates.'+module, globals(), locals(), ['*'])
    for itemname in dir(imp):
        item = getattr(imp, itemname)
        if isclass(item) and item != GraphTemplate and issubclass(item, GraphTemplate):
            template_objects.append(item())
            templates.append(module)
os.chdir(wd)

def list_target_types ():
    target_types = {}
    for t_o in template_objects:
        target_types.update(t_o.target_types)
    return target_types

def list_targets (metrics):
    targets = {}    
    for t_o in template_objects:
        targets.update(t_o.list_targets(metrics))
    return targets

def list_graphs (metrics):
    graphs = {}    
    for t_o in template_objects:
        graphs.update(t_o.list_graphs(metrics))
    return graphs

def parse_pattern(pattern):
    # if user doesn't specify any group_by, we automatically group by target_type and
    # by the tag specified by default_group_by in the target_type (which is a mandatory option)
    # if the user specified "group by foobar" in the pattern, we group by target_type and whatever the user said.
    group_by_match = re.search('(group by [^ ]+)',pattern)
    group_by = ['target_type']
    if group_by_match and group_by_match.groups() > 0:
        group_by.append(group_by_match.groups(1)[0].replace('group by ',''))
        pattern = pattern[:group_by_match.start(1)] + pattern[group_by_match.end(1):]
    else:
        group_by.append('default_group_by')
    # split pattern into multiple words which are all matched independently
    # this allows you write words in any order, and also makes it easy to use negations
    pattern = pattern.split()
    # if the pattern doesn't contain a "graph type specifier" like 'tpl' or 'targets',
    # assume we only want target ones. that sounds like good default behavior..
    if 'tpl' not in pattern and 'targets' not in pattern:
        pattern.append('target')
    pattern = {
        'pattern': pattern,
        'group_by': group_by
    }
    return pattern

# objects is expected to be a dict with elements like id: data
# id's are matched, and the return value is a dict in the same format
# every part of the pattern must match, use ! to negate
def match(objects, pattern):
    # prepare higher performing pattern structure
    # note that if you have twice the exact same "word" (ignoring leading '!'), the last one wins
    patterns = {}
    for patt in pattern['pattern']:
        negate = False
        if patt.startswith('!'):
            negate = True
            patt = patt[1:]
        patterns[patt] = {
            'negate': negate,
            'object': re.compile(patt)
        }
    
    objects_matching = {}
    for (id, data) in objects.items():
        match = True
        for patt in patterns.values():
            match_found = (patt['object'].search(id) is not None)
            if match_found and patt['negate']:
                match = False
            elif not match_found and not patt['negate']:
                match = False
        if match:
            objects_matching[id] = data
    return objects_matching

def load_metrics():
    f = open('metrics.json', 'r')
    return json.load(f)

@route('<path:re:/assets/.*>')
@route('<path:re:/graphitejs/.*js>')
@route('<path:re:/graphitejs/.*css>')
def static(path):
    return static_file(path, root='.')

@route('/', method='GET')
@route('/index', method='GET')
@route('/index/', method='GET')
@route('/index/<pattern>', method='GET')
def index(pattern = ''):
    output = template('page', body = template('body.index', pattern = pattern))
    return str(output)

@route('/index', method='POST')
def index_post():
    redirect('/index/%s' % request.forms.pattern)

@route('/debug')
def view_debug():
    metrics = load_metrics()
    target_types = list_target_types()
    targets = list_targets(metrics)
    graphs = list_graphs(metrics)
    graphs_targets, graphs_targets_options = build_graphs_from_targets(target_types, targets, {'group_by': ['target_type', 'default_group_by']})
    args = {'templates': templates,
        'targets': targets,
        'graphs': graphs,
        'graphs_targets': graphs_targets,
        'graphs_targets_options': graphs_targets_options
    }
    output = template('page', page = 'debug', body = template('body.debug', args))
    return str(output)

@route('/debug/metrics')
def debug_metrics():
    response.content_type = 'text/plain'
    return "\n".join(load_metrics())

# options must be a dict which contains at least a 'group_by' setting
def build_graphs_from_targets(target_types, targets, options):
    graphs = {}
    if not targets:
        return (graphs, options)
    group_by = options['group_by']
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
        target_type = target_data['tags']['target_type']
        if group_by[1] is 'default_group_by':
            group_by_tag = target_types[target_type]['default_group_by']
        else:
            group_by_tag = group_by[1]
        # group_by_tag is now something like 'server' or 'type', convert it to the actual value:
        group_by_tag = target_data['tags'][group_by_tag]
        constants = ['targets', target_type, group_by_tag]
        variables = []
        for tag_id in sorted(target_data['tags'].iterkeys()):
            tag_value = target_data['tags'][tag_id]
            if tag_value not in constants and tag_value:
                variables.append(tag_value)
        
        graph_title = '_'.join(constants)
        target_name = '_'.join(variables)
        if graph_title not in graphs:
            graph = target_types[target_type].get('default_graph_options',{}).copy()
            graph.update({'title': graph_title, 'targets': []})
            graphs[graph_title] = graph
        # set all options needed for graphitejs/flot:
        t = {
            'name': target_name,
            'target': target_data['target']
        }
        if 'color' in target_data: t['color'] = target_data['color']
        graphs[graph_title]['targets'].append(t)
    # given all graphs, process them to set any further options
    # nothing needed at this point.
    return (graphs, options)

@route('/graphs/', method='POST')
@route('/graphs/<pattern>', method='GET') # used for manually testing
def graphs(pattern = ''):
    '''
    get all relevant graphs matching pattern,
    graphs yielded by templates directly,
    enriched by combining the yielded targets
    '''
    if not pattern:
        pattern = request.forms.get('pattern')
    metrics = load_metrics()
    target_types = list_target_types()
    targets_all = list_targets(metrics)
    graphs_all = list_graphs(metrics)
    pattern = parse_pattern(pattern)
    targets_matching = match(targets_all, pattern)
    graphs_matching = match(graphs_all, pattern)
    graphs_targets_matching = build_graphs_from_targets(target_types, targets_matching, pattern)[0]
    len_targets_matching = len(targets_matching)
    len_graphs_matching = len(graphs_matching)
    len_graphs_targets_matching = len(graphs_targets_matching)
    graphs_matching.update(graphs_targets_matching)
    len_graphs_matching_all = len(graphs_matching)
    out = ''
    if len_graphs_matching_all > 0 and request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        out += template('snippet.graph-deps')
    out += "Pattern: '%s'<br/>" % pattern['pattern']
    out += "Group by: '%s'<br/>" % pattern['group_by']
    out += "# targets matching: %i/%i<br/>" % (len_targets_matching, len(targets_all))
    out += "# graphs matching: %i/%i<br/>" % (len_graphs_matching, len(graphs_all))
    out += "# graphs from matching targets: %i<br/>" % len_graphs_targets_matching
    out += "# total graphs: %i<br/>" % len_graphs_matching_all
    out += ''.join(template('snippet.graph', graphite_url = graphite_url, graph_name = title, graph_data = data) for (title, data) in graphs_matching.items())
    return out

# vim: ts=4 et sw=4:
