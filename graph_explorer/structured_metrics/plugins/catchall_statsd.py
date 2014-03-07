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
            'tags': {
                'unit': 'unknown',
                'source': 'statsd'
            }
        },
        {
            'match': '^stats\.timers\.(?P<tosplit>.*)',
            'tags': {
                'source': 'statsd'
            },
            'configure': lambda self, target: self.parse_statsd_timer(target)
        },
        {
            'match': '^stats\.(?P<tosplit>.*)',
            'target_type': 'rate',
            'tags': {
                'unit': 'unknown/s',
                'source': 'statsd'
            }
        },
        {
            'match': '^stats_counts\.(?P<tosplit>.*)',
            'target_type': 'count',
            'tags': {
                'unit': 'unknown',
                'source': 'statsd'
            }
        },
    ]

# vim: ts=4 et sw=4:
