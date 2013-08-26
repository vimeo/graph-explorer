import backend
from colors import colors


# convenience functions


def get_unique_tag_value(graph, target, tag):
    '''
    get a tag corresponding to a target, if it's clear the target "owns" the tag.
    this makes sure, if you're looking at cpu graphs with group by server,
    each cpu type (user, idle, etc) has a representative color
    but if you group by type (and compare servers on one graph for e.g. 'idle') you don't want
    all targets to have the same color... except if due to filtering only 1 server shows up, we
    can apply the color again
    '''
    t = None
    # the graph has other targets that have different values for this tag
    if tag in target['variables']:
        t = target['variables'][tag]
    elif len(graph['targets']) == 1:
        # there's no other targets in the graph, maybe due to a filter.
        # so we can safely get the value from [promoted] constants
        if tag in graph['constants']:
            t = graph['constants'][tag]
        elif tag in graph['promoted_constants']:
            t = graph['promoted_constants'][tag]
    return t


def get_tag_value(graph, target, tag):
    '''
    get a tag, if it applies to the target.  irrespective of other targets
    '''
    t = None
    if tag in target['variables']:
        t = target['variables'][tag]
    elif tag in graph['constants']:
        t = graph['constants'][tag]
    elif tag in graph['promoted_constants']:
        t = graph['promoted_constants'][tag]
    return t


def apply_colors(graph):
    '''
    update target colors in a clever, dynamic way. basically it's about defining
    colors for certain metrics (such as cpu idle metric = green), but since you
    can group by arbitrary things, you might have a graph comparing the idle
    values for different servers, in which case they should not be all green.

    # the graph will look something like:
        {
            'promoted_constants': {'type': 'update_time', 'plugin': 'carbon'},
            'from': '-24hours',
            'until': 'now',
            'constants': {'what': 'ms', 'target_type': 'gauge'},
            'targets': [
                {
                    'id': u'carbon.agents.dfvimeographite2-a.avgUpdateTime',
                    'variables': {'agent': u'dfvimeographite2-a'},
                    'target': u'carbon.agents.dfvimeographite2-a.avgUpdateTime'
                },
                (...)
            ]
        }
    '''

    color_assign_cpu = {
        'idle': colors['green'][0],
        'user': colors['blue'][0],
        'system': colors['blue'][1],
        'nice': colors['purple'][0],
        'softirq': colors['red'][0],
        'irq': colors['red'][1],
        'iowait': colors['orange'][0],
        'guest': colors['white'],
        'guest_nice': colors['white'],
        'steal': '#FFA791'  # brighter red
    }

    color_assign_mountpoint = {
        '_var': colors['red'][0],
        '_lib': colors['orange'][1],
        '_boot': colors['blue'][0],
        '_tmp': colors['purple'][0],
        'root': colors['green'][0]
    }

    color_assign_load = {
        '01': colors['red'][1],
        '05': colors['red'][0],
        '15': '#FFA791'  # brighter red
    }

    color_assign_timing = {
        'update_time': colors['turq'][0]
    }

    # http stuff, for swift and others
    color_assign_http = [
        ({'http_method': 'GET'},       colors['blue']),
        ({'http_method': 'HEAD'},      colors['yellow']),
        ({'http_method': 'PUT'},       colors['green']),
        ({'http_method': 'REPLICATE'}, colors['brown']),
        ({'http_method': 'DELETE'},    colors['red']),
    ]

    for (i, target) in enumerate(graph['targets']):
        if get_tag_value(graph, target, 'what') == 'cpu_state':
            t = get_unique_tag_value(graph, target, 'type')
            if t is not None:
                graph['targets'][i]['color'] = color_assign_cpu[t]

        if get_tag_value(graph, target, 'what') == 'ms':
            t = get_unique_tag_value(graph, target, 'type')
            if t in color_assign_timing:
                graph['targets'][i]['color'] = color_assign_timing[t]

        t = get_unique_tag_value(graph, target, 'mountpoint')
        if t is not None and t in color_assign_mountpoint:
            graph['targets'][i]['color'] = color_assign_mountpoint[t]

        if get_tag_value(graph, target, 'plugin') == 'load':
            t = get_unique_tag_value(graph, target, 'type')
            if t is not None and t in color_assign_load:
                graph['targets'][i]['color'] = color_assign_load[t]

        # swift
        w = get_tag_value(graph, target, 'what')
        if w == 'async_pendings':
            graph['targets'][i]['color'] = colors['turq'][0]

        # http.
        # note this doesn't prevent targets possibly having the same color
        m = get_tag_value(graph, target, 'http_method')
        if m is not None:
            t = {'http_method': m}
            for color in backend.get_action_on_rules_match(color_assign_http, t):
                # in some cases we want the color extra strong:
                if w in ('upper_90', 'errors'):
                    color = color[1]
                else:
                    color = color[0]
                graph['targets'][i]['color'] = color

    return graph
