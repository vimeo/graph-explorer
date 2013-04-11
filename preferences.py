count_interval = 60  # counts are in buckets of <size>s seconds; i.e. statsd flushInterval
timezone = "America/New_York"

# match on target properties (before matching) and apply settings accordingly
# this option doesn't actually work yet
target_options = [
        [
            {'server': 'df.*'},
            {'env': 'production'}
        ]
]

# match on graph properties (after matching) and apply settings accordingly
# all tags must match, if multiple tags are given in a list, they are OR'ed
graph_options = [
        [
            {'plugin': ['diskspace', 'memory'], 'what': 'bytes'},
            {'state': 'stacked', 'suffixes': 'binary'}
        ],
        [
            {'plugin': 'cpu'},
            {'state': 'stacked'}
        ],
        [
            {'what': 'freq_rel'},
            {'state': 'stacked'}
        ]
]
