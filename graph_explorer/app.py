#!/usr/bin/env python2
import bottle
from bottle import route, template, request, static_file, response, hook, BaseTemplate, post, redirect
import config
import preferences
from urlparse import urljoin
import structured_metrics
from graphs import Graphs
import graphs as g
from backend import Backend, make_config
from simple_match import filter_matching
from log import make_logger
from query import Query
from validation import RuleEditForm, RuleAddForm

import os
import traceback
from alerting import Db, rule_from_form


# contains all errors as key:(title,msg) items.
# will be used throughout the runtime to track all encountered errors
errors = {}

# will contain the latest data
last_update = None

config = make_config(config)

logger = make_logger('app', config)

logger.debug('app starting')
backend = Backend(config, logger)
s_metrics = structured_metrics.StructuredMetrics(config, logger)
graphs_manager = Graphs()
graphs_manager.load_plugins()
graphs_all = graphs_manager.list_graphs()

bottle.TEMPLATE_PATH.insert(0, os.path.dirname(__file__))


@route('<path:re:/assets/.*>')
@route('<path:re:/timeserieswidget/.*(js|css)>')
@route('<path:re:/timeserieswidget/timezone-js/src/.*js>')
@route('<path:re:/timeserieswidget/tz/.*>')
@route('<path:re:/DataTables/media/js/.*js>')
@route('<path:re:/DataTablesPlugins/integration/bootstrap/.*(js|css)>')
def static(path):
    return static_file(path, root=os.path.dirname(__file__))


@route('/', method='GET')
@route('/index', method='GET')
@route('/index/', method='GET')
@route('/index/<query:path>', method='GET')
def index(query=''):
    body = template('templates/body.index', errors=errors, query=query)
    return render_page(body)


@route('/dashboard/<dashboard_name>')
@route('/dashboard/<dashboard_name>/')
@route('/dashboard/<dashboard_name>/<apply_all_from_url>', method='GET')
def slash_dashboard(dashboard_name=None, apply_all_from_url=''):
    dashboard = template('templates/dashboards/%s' % dashboard_name, errors=errors, apply_all_from_url=apply_all_from_url)
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
            }
    body = template('templates/body.inspect', args)
    return render_page(body, 'inspect')


@route('/api/<query:path>', method='GET')
def api(query=''):
    try:
        query = Query(query)
        (query, targets_matching) = s_metrics.matching(query)
    except Exception, e:  # pylint: disable=W0703
        return e

    tags = set()
    for target in targets_matching.values():
        for tag_name in target['tags'].keys():
            tags.add(tag_name)
    graphs_matching = filter_matching(query['ast'], graphs_all)
    graphs_matching = g.build(graphs_matching, query)
    stats = {'len_targets_all': s_metrics.count_metrics(),
             'len_graphs_all': len(graphs_all),
             'len_targets_matching': len(targets_matching),
             'len_graphs_matching': len(graphs_matching),
             }
    graphs = []
    targets_list = {}
    if query['statement'] in ('graph', 'lines', 'stack'):
        graphs_targets_matching = g.build_from_targets(targets_matching, query, preferences)[0]
        stats['len_graphs_targets_matching'] = len(graphs_targets_matching)
        graphs_matching.update(graphs_targets_matching)
        stats['len_graphs_matching_all'] = len(graphs_matching)
        for key in sorted(graphs_matching.iterkeys()):
            graphs.append((key, graphs_matching[key]))
    elif query['statement'] == 'list':
        # for now, only supports targets, not graphs
        targets_list = targets_matching
        stats['len_graphs_targets_matching'] = 0
        stats['len_graphs_matching_all'] = 0

    del query['target_modifiers']  # callback functions that are not serializable
    args = {'errors': errors,
            'query': query,
            'graphs': graphs,
            'targets_list': targets_list,
            'tags': list(tags),
            }
    args.update(stats)
    return args


@route('/graphs/', method='POST')
@route('/graphs/<query:path>', method='GET')  # used for manually testing
def graphs_nodeps(query=''):
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
    import urllib2
    url = urljoin(config.graphite_url_server, "/render/" + query)
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


@route('/rules')
@route('/rules/')
def rules_list():
    db = Db(config.alerting_db)
    if 'rules' in errors:
        del errors['rules']
    try:
        body = template('templates/body.rules', errors=errors, rules=db.get_rules())
    except Exception, e:
        errors['rules'] = ("Couldn't list rules: %s" % e, traceback.format_exc())
    if errors:
        body = template('templates/snippet.errors', errors=errors)
        return render_page(body)
    return render_page(body, 'rules')


@route('/rules/edit/<Id>')
@post('/rules/edit')
def rules_edit(Id=None):
    db = Db(config.alerting_db)
    if Id is not None:
        rule = db.get_rule(int(Id))
    else:
        rule = db.get_rule(int(request.forms['Id']))
    form = RuleEditForm(request.forms, rule)
    if request.method == 'POST' and form.validate():
        try:
            if 'rules_add' in errors:
                del errors['rules_add']
            form.populate_obj(rule)
            db = Db(config.alerting_db)
            db.edit_rule(rule)
        except Exception, e:  # pylint: disable=W0703
            errors["rules_add"] = ("Couldn't add rule: %s" % e, traceback.format_exc())
        return redirect('/rules')
    args = {'errors': errors,
            'form': form
            }
    body = template('templates/body.rules_edit', args)
    return render_page(body, 'rules_edit')


@route('/rules/add')
@route('/rules/add/')
@route('/rules/add/<expr>')
@post('/rules/add')
def rules_add(expr=''):
    form = RuleAddForm(request.forms)
    if request.method == 'GET':
        form.expr.data = expr
    if request.method == 'POST' and form.validate():
        try:
            if 'rules_add' in errors:
                del errors['rules_add']
            rule = rule_from_form(form)
            db = Db(config.alerting_db)
            db.add_rule(rule)
        except Exception, e:  # pylint: disable=W0703
            errors["rules_add"] = ("Couldn't add rule: %s" % e, traceback.format_exc())
        return redirect('/rules')
    args = {'errors': errors,
            'form': form
            }
    body = template('templates/body.rules_add', args)
    return render_page(body, 'rules_add')


@route('/rules/view/<Id>')
def rules_view(Id):
    db = Db(config.alerting_db)
    rule = db.get_rule(int(Id))
    body = template('templates/body.rule', errors=errors, rule=rule)
    return render_page(body)


@route('/rules/delete/<Id>')
def rules_delete(Id):
    db = Db(config.alerting_db)
    try:
        db.delete_rule(int(Id))
    except Exception, e:  # pylint: disable=W0703
        errors["rules_delete"] = ("Couldn't delete rule: %s" % e, traceback.format_exc())
    if errors:
        body = template('templates/snippet.errors', errors=errors)
        return render_page(body)
    return redirect('/rules')


@hook('before_request')
def seedviews():
    # templates need to know the relative path to get resources from
    root = '../' * request.path.count('/')
    BaseTemplate.defaults['root'] = root
    BaseTemplate.defaults['config'] = config
    BaseTemplate.defaults['preferences'] = preferences


def handle_graphs_minimal(query, deps):
    '''
    like handle_graphs(), but without extra decoration, so can be used on
    dashboards
    TODO dashboard should show any errors
    '''
    if not query:
        return template('templates/graphs', query=query, errors=errors)
    return render_graphs(query, minimal=True, deps=deps)


def render_graphs(query, minimal=False, deps=False):
    if "query_parse" in errors:
        del errors["query_parse"]
    try:
        query = Query(query)
    except Exception, e:  # pylint: disable=W0703
        errors["query_parse"] = ("Couldn't parse query: %s" % e, traceback.format_exc())
    if errors:
        body = template('templates/snippet.errors', errors=errors)
        return render_page(body)

    # TODO: something goes wrong here.
    # if you do a query that will give an ES error (say 'foo(')
    # and then fix the query and hit enter, this code will see the new query
    # and ES will process the query fine, but for some reason the old error
    # doesn't clear and sticks instead.

    if "match_metrics" in errors:
        del errors["match_metrics"]
    try:
        (query, targets_matching) = s_metrics.matching(query)
        # presentation overrides. useful to make screenshots etc with
        # specific query settings not visible in the UI
        # query['from'] = "-3weeks"
        # query['to'] = "-2weeks"
    except Exception, e:  # pylint: disable=W0703
        errors["match_metrics"] = ("Couldn't find matching metrics: %s" % e, traceback.format_exc())
    if errors:
        body = template('templates/snippet.errors', errors=errors)
        return render_page(body)

    tags = set()
    for target in targets_matching.values():
        for tag_name in target['tags'].keys():
            tags.add(tag_name)
    graphs_matching = filter_matching(query['ast'], graphs_all)
    graphs_matching = g.build(graphs_matching, query)
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
        graphs_targets_matching = g.build_from_targets(targets_matching, query, preferences)[0]
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
            'graphs': graphs,
            'targets_list': targets_list,
            'tags': tags,
            }
    args.update(stats)
    if minimal:
        out += template('templates/graphs_minimal', args)
    else:
        out += template('templates/graphs', args)
    return out


# vim: ts=4 et sw=4:
