#!/usr/bin/env python2
import os, json, sys, traceback, re
from bottle import route, run, debug, template, request, validate, static_file, redirect
from config import *

# this bit of code should be more dynamic but that goes beyond my python-fu
# we basically want to import all templates in a given directory, instantiate objects from their classes,
# and keep a list of all of them
from graph_templates.cpu import CpuTemplate
t = CpuTemplate()
templates = ["cpu"]

def match(graphs, pattern):
    """
    replace ' ' with '.*' and use as regex, allows easy but powerful matching
    """
    pattern = pattern.replace(' ','.*')
    object = re.compile(pattern)
    for (graph,url) in graphs.items():
            match = object.search(graph)
            if match is not None:
                yield (graph,url)

def load_metrics():
    f = open('metrics.json', 'r')
    return json.load(f)

@route('/assets/:path#.*#')
def static(path):
    return static_file(path, root='assets')

@route('/', method='GET')
@route('/index', method='GET')
@route('/index/', method='GET')
@route('/index/:pattern', method='GET')
def index(pattern = ''):
    metrics = load_metrics()
    graphs = t.build_graphs(metrics)
    graphs_js = '["%s"]' % '","'.join(graphs.keys()) # something like ["graph1","graph2","graph3"]
    output = template('page', body = template('body.index', graphs_js = graphs_js, pattern = pattern))
    return str(output)

@route('/index', method='POST')
def index_post():
    redirect('/index/%s' % request.forms.pattern)

@route('/debug')
def view_debug():
    metrics = load_metrics()
    graphs = t.build_graphs(metrics)
    output = template('page', body = template('body.debug', metrics = metrics, templates = templates, graphs = graphs))
    return str(output)

@route('/graphs/', method='POST')
def graphs():
    pattern = request.forms.get('pattern')
    metrics = load_metrics()
    graphs = t.build_graphs(metrics)
    out = ''
    for i in [template('snippet.graph', base_url = base_url, graph = graph, url = url) for (graph, url) in match(graphs, pattern)]:
        out += i
    if not out:
        out = "No graphs matching pattern '%s'" % pattern
    return str(out)

debug(True)
run(reloader=True, host=listen_host)

# vim: ts=4 et sw=4:
