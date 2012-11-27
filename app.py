#!/usr/bin/env python2
import os, json, sys, traceback, re
from bottle import route, run, debug, template, request, validate, static_file, redirect
from config import *

# this bit of code should be more dynamic but that goes beyond my python-fu
# we basically want to import all templates in a given directory, instantiate objects from their classes,
# and keep a list of all of them
from graph_templates.cpu import CpuTemplate
from graph_templates.swift_object import SwiftObjectTemplate
template_objects = [CpuTemplate(), SwiftObjectTemplate()]
templates = ["cpu", "swift_object"]

def build_graphs (metrics):
    graphs = {}    
    for t_o in template_objects:
        graphs.update(t_o.build_graphs(metrics))
    return graphs

def match(graphs, pattern):
    """
    replace ' ' with '.*' and use as regex, allows easy but powerful matching
    """
    pattern = pattern.replace(' ','.*')
    object = re.compile(pattern)
    for (name, data) in graphs.items():
            match = object.search(name)
            if match is not None:
                yield (name,data)

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
    metrics = load_metrics()
    graphs = build_graphs(metrics)
    graphs_js = '["%s"]' % '","'.join(graphs.keys()) # something like ["graph1","graph2","graph3"]
    output = template('page', body = template('body.index', graphs_js = graphs_js, pattern = pattern))
    return str(output)

@route('/index', method='POST')
def index_post():
    redirect('/index/%s' % request.forms.pattern)

@route('/debug')
def view_debug():
    metrics = load_metrics()
    graphs = build_graphs(metrics)
    output = template('page', page = 'debug', body = template('body.debug', metrics = metrics, templates = templates, graphs = graphs))
    return str(output)

@route('/graphs/', method='POST')
@route('/graphs/<pattern>', method='GET') # used for manually testing
def graphs(pattern = ''):
    if not pattern:
        pattern = request.forms.get('pattern')
    metrics = load_metrics()
    graphs = build_graphs(metrics)
    out = ''.join(template('snippet.graph', base_url = base_url, graph_name = graph_name, graph_data = graph_data) for (graph_name, graph_data) in match(graphs, pattern))
    if out and request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        out = template('snippet.graph-deps') + out
    if not out:
        out = "No graphs matching pattern '%s'" % pattern
    return out

debug(True)
run(reloader=True, host=listen_host)

# vim: ts=4 et sw=4:
