count_interval = 60  # counts are in buckets of <size>s seconds; i.e. statsd flushInterval
timezone = "America/New_York"

from preferences_color import apply_colors
# match on graph properties (after targets are matched and graph is built)
# and apply options accordingly.
# if options is a dict, merge it into the graph. if it's a function, the graph
# gets passed and the return value is used as new graph definition.
# all tags must match, if multiple tags are given in a list, they are OR'ed
# multiple matches can occur, they are performed in order.
graph_options = [
    [
        {'where': 'system_memory', 'unit': 'B'},  # match
        {'state': 'stacked', 'suffixes': 'binary'}  # set option
    ],
    [
        {'plugin': 'diskspace', 'unit': 'B'},
        {'state': 'stacked', 'suffixes': 'binary'}
    ],
    [
        {'what': 'cpu_usage'},
        {'state': 'stacked'}
    ],
    [
        {'unit': ['freq_rel', 'freq_abs']},
        {'state': 'stacked'}
    ],
    [
        {'unit': 'P'},  # probabilities between 0 and 1
        {'yaxis': {'max': 1}}
    ],
    [
        {},
        apply_colors
    ]
]
