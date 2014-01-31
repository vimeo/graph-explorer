from colors import colors
from backend import get_action_on_rules_match


# convenience functions


def get_unique_tag_value(graph, target, tag):
    '''
    get a tag corresponding to a target, if it's clear the target "owns" the tag.
    this makes sure, if you're looking at cpu graphs with group by server,
    each cpu type (user, idle, etc) has a representative color
    but if you group by type (and compare servers on one graph for e.g. 'idle') you don't want
    all targets to have the same color... except if due to filtering only 1 server shows up, we
    can apply the color again.
    note that if the graph has 6 targets: 3 different servers, each 2 different types, then this
    will proceed and you'll see 3 targets of each color.
    this could be extended to search for the value in the variables of all other targets, to guarantee
    uniqueness (and avoid a color showing up multiple times)
    TLDR: color a target based on tag value, but avoid all targets having the same color on 1 graph
    '''
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
        else:
            return None
    else:
        return None

    # t can be a tuple if it's an aggregated tag
    if isinstance(t, basestring):
        return t
    else:
        return t[0]


def get_tag_value(graph, target, tag):
    '''
    get a tag, if it applies to the target.  irrespective of other targets
    i.e. color a target based on tag value, and don't try to avoid multiple targets with same color
    on 1 graph.
    '''
    if tag in target['variables']:
        t = target['variables'][tag]
    elif tag in graph['constants']:
        t = graph['constants'][tag]
    elif tag in graph['promoted_constants']:
        t = graph['promoted_constants'][tag]
    else:
        return None
    if isinstance(t, basestring):
        return t
    else:
        return t[0]


def bin_set_color(graph, target):
    if 'bin_upper' not in target['tags']:
        return
    # later we could do a real green-to-red interpolation by looking at
    # the total range (all bin_uppers in the entire class) and computing
    # a color, maybe using something like color_variant("#FF0000", -150),
    # for now, this will have to do
    bin_upper = target['tags']['bin_upper']
    colormap = {
        '0.01': '#2FFF00',
        '0.05': '#64DD0E',
        '0.1': '#9CDD0E',
        '0.5': '#DDCC0E',
        '1': '#DDB70E',
        '5': '#FF6200',
        '10': '#FF3C00',
        '50': '#FF1E00',
        'inf': '#FF0000'
    }
    if bin_upper in colormap:
        target['color'] = colormap[bin_upper]


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
            'constants': {'unit': 'ms', 'target_type': 'gauge'},
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

    # color targets based on tags, even when due to grouping metrics with the same tags (colors)
    # show up on the same graph
    rules_tags = [
        # http stuff, for swift and others
        [
            {},
            {
                'http_method': {
                    'GET': colors['blue'][0],
                    'HEAD': colors['yellow'][0],
                    'PUT': colors['green'][0],
                    'REPLICATE': colors['brown'][0],
                    'DELETE': colors['red'][0]
                }
            }
        ],
        [
            {'stat': ['upper', 'upper_90']},
            {
                'http_method': {
                    'GET': colors['blue'][1],
                    'HEAD': colors['yellow'][1],
                    'PUT': colors['green'][1],
                    'REPLICATE': colors['brown'][1],
                    'DELETE': colors['red'][1]
                }
            }
        ],
    ]

    # color targets based on tags, except when due to grouping metrics
    # with the same tags show up on the same graph
    rules_unique_tags = [
        [
            {'what': 'cpu_usage'},
            {
                'type': {
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
            }
        ],
        [
            {},
            {
                'mountpoint': {
                    '_var': colors['red'][0],
                    '_lib': colors['orange'][1],
                    '_boot': colors['blue'][0],
                    '_tmp': colors['purple'][0],
                    'root': colors['green'][0]
                }
            }
        ],
        [
            {'plugin': 'load'},
            {
                'type': {
                    '01': colors['red'][1],
                    '05': colors['red'][0],
                    '15': '#FFA791'  # brighter red
                }
            }
        ],
        [
            {'unit': 'ms'},
            {
                'type': {
                    'update_time': colors['turq'][0]
                }
            }
        ],
        [
            {'unit': 'freq_abs'},
            bin_set_color
        ]
    ]

    for target in graph['targets']:
        tags = dict(graph['constants'].items() + graph['promoted_constants'].items() + target['variables'].items())

        for action in get_action_on_rules_match(rules_unique_tags, tags):
            if callable(action):  # hasattr(action, '__call__'):
                action(graph, target)
            else:
                for (tag_key, matches) in action.items():
                    t = get_unique_tag_value(graph, target, tag_key)
                    if t is not None and t in matches:
                        target['color'] = matches[t]

        for action in get_action_on_rules_match(rules_tags, target):
            for (tag_key, matches) in action.items():
                t = get_tag_value(graph, target, tag_key)
                if t is not None and t in matches:
                    target['color'] = matches[t]

    return graph
