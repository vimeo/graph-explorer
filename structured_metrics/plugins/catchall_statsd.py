from . import Plugin


class CatchallStatsdPlugin(Plugin):
    """
    Like catchall, but for targets from statsd (presumably)
    """
    priority = -4

    targets = [
        {
            'match': '^stats\.gauges\.(?P<tosplit>.*)',
            'target_type': 'gauge',
            'configure': [
                lambda self, target: self.add_tag(target, 'unit', 'unknown'),
                lambda self, target: self.add_tag(target, 'source', 'statsd'),
                lambda self, target: self.autosplit(target)
            ]
        },
        {
            'match': '^stats\.timers\.(?P<tosplit>.*)',
            'target_type': 'gauge',
            'configure': [
                lambda self, target: self.parse_statsd_timer(target),
                lambda self, target: self.add_tag(target, 'source', 'statsd'),
                lambda self, target: self.autosplit(target)
            ]
        },
        {
            'match': '^stats\.(?P<tosplit>.*)',
            'target_type': 'rate',
            'configure': [
                lambda self, target: self.add_tag(target, 'unit', 'unknown/s'),
                lambda self, target: self.add_tag(target, 'source', 'statsd'),
                lambda self, target: self.autosplit(target)
            ]
        },
        {
            'match': '^stats_counts\.(?P<tosplit>.*)',
            'target_type': 'count',
            'configure': [
                lambda self, target: self.add_tag(target, 'unit', 'unknown'),
                lambda self, target: self.add_tag(target, 'source', 'statsd'),
                lambda self, target: self.autosplit(target)
            ]
        },
    ]

# vim: ts=4 et sw=4:
