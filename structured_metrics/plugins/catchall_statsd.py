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
            # (and no no_match), but i think that makes the regex slower
            'match': '^stats\.timers\.(?P<n1>[^\.]+)\.?(?P<n2>[^\.]*)\.?(?P<n3>[^\.]*)\.?(?P<n4>[^\.]*)\.?(?P<n5>[^\.]*)\.?(?P<n6>[^\.]*)\.?(?P<n7>[^\.]*)\.(?P<upper_limit>[^\.]+)$',
            'no_match': '\.count$',
            'target_type': 'gauge',
            'targets': [
                {
                    'configure': [
                        lambda self, target: self.add_tag(target, 'what', 'freq'),
                        lambda self, target: self.add_tag(target, 'type', 'absolute'),
                        lambda self, target: self.add_tag(target, 'source', 'statsd')
                    ]
                },
                {
                    'configure': [
                        lambda self, target: self.add_tag(target, 'what', 'freq'),
                        lambda self, target: self.add_tag(target, 'type', 'relative'),
                        lambda self, target: self.add_tag(target, 'source', 'statsd'),
                        lambda self, target: {'target': 'divideSeries(%s,%s)' % (target['target'],target['target'].replace(target['tags']['upper_limit'],'count'))}
                    ]
                }
            ]

        },
        {
            # TODO: for some reason the 'count' at the end makes this regex quite slow
            # you can see this in StructuredMetrics.list_targets if you print
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
