import os
from inspect import isclass
from ..structured_metrics import PluginError
from ..backend import get_action_on_rules_match
from ..target import Target
from .. import target as t
from .. import convert
from ..query import Query


class Graphs(object):

    def __init__(self):
        self.plugins = []

    def load_plugins(self):
        '''
        loads all the plugins sub-modules
        returns encountered errors, doesn't raise them because
        whoever calls this function defines how any errors are
        handled. meanwhile, loading must continue
        '''
        from .plugins import Plugin
        from . import plugins
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
            except Exception, e:  # pylint: disable=W0703
                errors.append(PluginError(module, "Failed to add plugin '%s'" % module, e))
                continue

            for itemname in dir(imp):
                item = getattr(imp, itemname)
                if isclass(item) and item != Plugin and issubclass(item, Plugin):
                    try:
                        self.plugins.append((module, item()))
                    except Exception, e:  # pylint: disable=W0703
                        errors.append(PluginError(module, "Failed to add plugin '%s'" % module, e))
        os.chdir(wd)
        # sort plugins by their priority
        self.plugins = sorted(self.plugins, key=lambda t: t[1].priority, reverse=True)
        return errors

    def list_graphs(self):
        graphs = {}
        for plugin in self.plugins:
            _plugin_name, plugin_object = plugin
            graphs.update(plugin_object.get_graphs())
        return graphs


def build(graphs, query):
    for v in graphs.values():
        v.update(query)
    return graphs


def limit_targets(nolimit_graphs, limit):
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


def build_from_targets(targets, query, preferences):
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
            query['target_modifiers'].append(
                Query.graphite_function_applier('movingAverage', avg_over_amount * multiplier))

    # for each group_by bucket, make 1 graph.
    # so for each graph, we have:
    # the "constants": tags in the group_by
    # the "variables": tags not in the group_by, which can have arbitrary
    # values, or different values from a group_by tag that match the same
    # bucket pattern
    # go through all targets and group them into graphs:
    for _target_id, target_data in sorted(targets.items()):
        # FWIW. has an 'id' which timeserieswidget doesn't care about
        target = Target(target_data)
        target['target'] = target['id']

        (graph_key, constants) = target.get_graph_info(group_by)
        if graph_key not in graphs:
            graph = {'from': query['from'], 'until': query['to']}
            graph.update({'constants': constants, 'targets': []})
            graphs[graph_key] = graph
        graphs[graph_key]['targets'].append(target)

    # ok so now we have a graphs dictionary with a graph for every appropriate
    # combination of group_by tags, and each graph contains all targets that
    # should be shown on it.  but the user may have asked to aggregate certain
    # targets together, by summing and/or averaging across different values of
    # (a) certain tag(s). let's process the aggregations now.
    if (sum_by or avg_by):
        for (graph_key, graph_config) in graphs.items():
            graph_config['targets_sum_candidates'] = {}
            graph_config['targets_avg_candidates'] = {}
            graph_config['normal_targets'] = []

            # process equivalence rules, see further down.
            filter_candidates = {}
            for tag, buckets in sum_by.items():

                # first separate the individuals from the _sum_

                filter_candidates[tag] = {}
                for target in graph_config['targets']:
                    # we can use agg_key to find out if they all have the same values
                    # other than this one particular key
                    key = target.get_agg_key({tag: buckets})
                    if key not in filter_candidates[tag]:
                            filter_candidates[tag][key] = {
                                'individuals': []
                            }
                    if target['tags'].get(tag, '') == '_sum_':
                        filter_candidates[tag][key]['_sum_'] = target
                    else:
                        filter_candidates[tag][key]['individuals'].append(target)

                # for all agg keys that only have the '' bucket,
                # if targets are identical except that some have tag
                # foo={bar,baz,0,quux, ...} and one of them has foo=_sum_ and we're
                # summing by that tag, and we didn't filter on foo,
                # remove all the ones except the sum one

                if len(buckets) == 1 and buckets[0] == '':
                    if not Query.filtered_on(query, tag):
                        for key in filter_candidates[tag].keys():
                            if '_sum_' in filter_candidates[tag][key]:
                                for i in filter_candidates[tag][key]['individuals']:
                                    graph_config['targets'].remove(i)

                # if we are summing, and we have a filter, and we have individual ones and a _sum_, remove the _sum_
                # irrespective of buckets.  note that this removes the _sum_ target without the user needing to filter it out explicitly
                # this is the only place we do that, but it makes sense.  we wouldn't want users to specify the _sum_ removal explicitly
                # all the time, esp for multiple tag keys
                if Query.filtered_on(query, tag):
                    for key in filter_candidates[tag].keys():
                        if '_sum_' in filter_candidates[tag][key]:
                            graph_config['targets'].remove(filter_candidates[tag][key]['_sum_'])

            for target in graph_config['targets']:
                sum_id = target.get_agg_key(sum_by)
                if sum_id:
                    if sum_id not in graph_config['targets_sum_candidates']:
                        graphs[graph_key]['targets_sum_candidates'][sum_id] = []
                    graph_config['targets_sum_candidates'][sum_id].append(target)

            for (sum_id, targets) in graph_config['targets_sum_candidates'].items():
                if len(targets) > 1:
                    for candidate in targets:
                        graph_config['targets'].remove(candidate)
                    graph_config['targets'].append(
                        t.graphite_func_aggregate(targets, sum_by, "sumSeries"))

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
                    for candidate in targets:
                        graph_config['targets'].remove(candidate)
                    graph_config['targets'].append(
                        t.graphite_func_aggregate(targets, avg_by, "averageSeries"))

    # remove targets/graphs over the limit
    graphs = limit_targets(graphs, query['limit_targets'])

    # Apply target modifiers (like movingAverage, summarize, ...)
    for (graph_key, graph_config) in graphs.items():
        for target in graph_config['targets']:
            for target_modifier in query['target_modifiers']:
                target_modifier(target, graph_config)

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
        graph_config['promoted_constants'] = {}
        for tag_name in effective_constants:
            graph_config['promoted_constants'][tag_name] = first_values_seen[tag_name]
            for target in graph_config['targets']:
                target['variables'].pop(tag_name, None)

        # now that graph config is "rich", merge in settings from preferences
        constants = dict(graph_config['constants'].items() + graph_config['promoted_constants'].items())
        for graph_option in get_action_on_rules_match(preferences.graph_options, constants):
            if isinstance(graph_option, dict):
                graph_config.update(graph_option)
            else:
                graph_config = graphs[graph_key] = graph_option(graph_config)

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
    # note that we can't just compile constants + promoted_constants,
    # part of the original graph key is also set by the group by (which, by
    # means of the bucket patterns doesn't always translate into constants),
    # we solve this by just including the old key.
    new_graphs = {}
    for (graph_key, graph_config) in graphs.items():
        new_key = ','.join('%s=%s' % i for i in graph_config['promoted_constants'].items())
        new_key = '%s__%s' % (graph_key, new_key)
        new_graphs[new_key] = graph_config
    graphs = new_graphs

    return (graphs, query)
