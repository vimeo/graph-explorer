from . import Plugin


class CatchallStatsdPlugin(Plugin):
    priority = -4
    """
    Like catchall, but for targets from statsd (presumably)
    """

    targets = [
        {
            'match': '^stats\.gauges\.(?P<n1>[^\.]+)\.?(?P<n2>[^\.]*)\.?(?P<n3>[^\.]*)\.?(?P<n4>[^\.]*)\.?(?P<n5>[^\.]*)\.?(?P<n6>[^\.]*)\.?(?P<n7>[^\.]*)$',
            'target_type': 'gauge',
            'configure': [
                lambda self, target: self.add_tag(target, 'what', 'unknown'),
                lambda self, target: self.add_tag(target, 'source', 'statsd')
            ]
        },
        {
            'match': '^stats\.timers\.(?P<n1>[^\.]+)\.?(?P<n2>[^\.]*)\.?(?P<n3>[^\.]*)\.?(?P<n4>[^\.]*)\.?(?P<n5>[^\.]*)\.?(?P<n6>[^\.]*)\.?(?P<n7>[^\.]*)\.(?P<type>[^\.]+)$',
            'no_match': ['\.count$', '\.bin_[^\.]+$'],
            'target_type': 'gauge',
            'configure': [
                lambda self, target: self.add_tag(target, 'what', 'ms'),
                lambda self, target: self.add_tag(target, 'source', 'statsd')
            ]
        },
        {
            # we could of course do \.bin_(?P<upper_limit>[^\.]+)$ at the end
            # (and no no_match), but that's slow :( computation time from 2 ->
            # 6 minutes
            'match': '^stats\.timers\.(?P<n1>[^\.]+)\.?(?P<n2>[^\.]*)\.?(?P<n3>[^\.]*)\.?(?P<n4>[^\.]*)\.?(?P<n5>[^\.]*)\.?(?P<n6>[^\.]*)\.?(?P<n7>[^\.]*)\.(?P<upper_limit>[^\.]+)$',
            'no_match': '\.(count|lower|mean|mean_90|std|sum|sum_90|upper|upper_90)$',
            'target_type': 'gauge',
            'configure': [
                lambda self, target: self.add_tag(target, 'what', 'freq_abs'),
                lambda self, target: self.add_tag(target, 'source', 'statsd')
            ]

        },
        {
            # TODO: for some reason the 'count' at the end makes this regex quite slow
            # you can see this in StructuredMetrics.list_metrics if you print
            # something for every metric. timers will be very slowly. if you
            # make it (?P<type>[^\.]+) it becomes fast again, but we need to
            # match on only the ones ending on count :(
            'match': '^stats\.timers\.(?P<n1>[^\.]+)\.?(?P<n2>[^\.]*)\.?(?P<n3>[^\.]*)\.?(?P<n4>[^\.]*)\.?(?P<n5>[^\.]*)\.?(?P<n6>[^\.]*)\.?(?P<n7>[^\.]*)\.count$',
            'target_type': 'count',
            'configure': [
                lambda self, target: self.add_tag(target, 'what', 'packets'),
                lambda self, target: self.add_tag(target, 'type', 'timer'),
                lambda self, target: self.add_tag(target, 'source', 'statsd')
            ]
        },
        {
            'match': '^stats\.(?P<n1>[^\.]+)\.?(?P<n2>[^\.]*)\.?(?P<n3>[^\.]*)\.?(?P<n4>[^\.]*)\.?(?P<n5>[^\.]*)\.?(?P<n6>[^\.]*)\.?(?P<n7>[^\.]*)$',
            'no_match': '^stats\.timers\.',
            'target_type': 'rate',
            'configure': [
                lambda self, target: self.add_tag(target, 'what', 'unknown'),
                lambda self, target: self.add_tag(target, 'source', 'statsd')
            ]
        },
        {
            'match': '^stats_counts\.(?P<n1>[^\.]+)\.?(?P<n2>[^\.]*)\.?(?P<n3>[^\.]*)\.?(?P<n4>[^\.]*)\.?(?P<n5>[^\.]*)\.?(?P<n6>[^\.]*)\.?(?P<n7>[^\.]*)$',
            'target_type': 'count',
            'configure': [
                lambda self, target: self.add_tag(target, 'what', 'unknown'),
                lambda self, target: self.add_tag(target, 'source', 'statsd')
            ]
        },
    ]


# vim: ts=4 et sw=4:
