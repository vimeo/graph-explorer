from . import Plugin


class CatchallStatsdPlugin(Plugin):
    priority = -4
    """
    Like catchall, but for targets from statsd (presumably)
    """

    targets = [
        {
            'match': '^stats\.gauges\.?(?P<n1>[^\.]*)\.?(?P<n2>[^\.]*)\.?(?P<n3>[^\.]*)\.?(?P<n4>[^\.]*)\.?(?P<n5>[^\.]*)\.?(?P<n6>[^\.]*)\.?(?P<n7>[^\.]*)$',
            'target_type': 'gauge',
            'configure': [
                lambda self, target: self.add_tag(target, 'what', 'unknown'),
                lambda self, target: self.add_tag(target, 'source', 'statsd')
            ]
        },
        {
            'match': '^stats\.timers\.?(?P<n1>[^\.]*)\.?(?P<n2>[^\.]*)\.?(?P<n3>[^\.]*)\.?(?P<n4>[^\.]*)\.?(?P<n5>[^\.]*)\.?(?P<n6>[^\.]*)\.?(?P<n7>[^\.]*)$',
            'target_type': 'gauge',
            'configure': [
                lambda self, target: self.add_tag(target, 'what', 'unknown'),
                lambda self, target: self.add_tag(target, 'source', 'statsd')
            ]
        },
        {
            'match': '^stats\.?(?P<n1>[^\.]*)\.?(?P<n2>[^\.]*)\.?(?P<n3>[^\.]*)\.?(?P<n4>[^\.]*)\.?(?P<n5>[^\.]*)\.?(?P<n6>[^\.]*)\.?(?P<n7>[^\.]*)$',
            'target_type': 'rate',
            'configure': [
                lambda self, target: self.add_tag(target, 'what', 'unknown'),
                lambda self, target: self.add_tag(target, 'source', 'statsd')
            ]
        },
        {
            'match': '^stats_counts\.?(?P<n1>[^\.]*)\.?(?P<n2>[^\.]*)\.?(?P<n3>[^\.]*)\.?(?P<n4>[^\.]*)\.?(?P<n5>[^\.]*)\.?(?P<n6>[^\.]*)\.?(?P<n7>[^\.]*)$',
            'target_type': 'count',
            'configure': [
                lambda self, target: self.add_tag(target, 'what', 'unknown'),
                lambda self, target: self.add_tag(target, 'source', 'statsd')
            ]
        },
    ]


# vim: ts=4 et sw=4:
