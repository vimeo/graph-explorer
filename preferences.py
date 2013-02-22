count_interval = 60  # counts are in buckets of <size>s seconds; i.e. statsd flushInterval
timezone = "America/New_York"
# match on graph properties and apply settings accordingly
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
            {'what': 'freq', 'type': 'relative'},
            {'state': 'stacked'}
        ]
]
