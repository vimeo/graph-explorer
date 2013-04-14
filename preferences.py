count_interval = 60  # counts are in buckets of <size>s seconds; i.e. statsd flushInterval
timezone = "America/New_York"

# match on target properties (before matching) and apply settings accordingly
# this option doesn't actually work yet
target_options = [
    [
        {'server': 'df.*'},  # match
        {'env': 'production'}  # set option
    ]
]

from preferences_color import apply_colors
# match on graph properties (after matching) and apply options accordingly.
# if options is a dict, merge it into the graph. if it's a function, the graph
# gets passed and the return value is used as new graph definition.
# all tags must match, if multiple tags are given in a list, they are OR'ed
graph_options = [
    [
        {'plugin': ['diskspace', 'memory'], 'what': 'bytes'},  # match
        {'state': 'stacked', 'suffixes': 'binary'}  # set option
    ],
    [
        {'plugin': 'cpu'},
        {'state': 'stacked'}
    ],
    [
        {'what': 'freq_rel'},
        {'state': 'stacked'}
    ],
    [
        {},
        apply_colors
    ]
]

