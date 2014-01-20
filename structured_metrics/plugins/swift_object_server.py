from . import Plugin


class SwiftObjectServerPlugin(Plugin):

    targets = [
        {
            'match': '^stats\.timers\.(?P<server>[^\.]+)\.(?P<swift_type>object)-server\.(?P<http_method>[^\.]+)\.timing\.(?P<autosplit>[^\.]+)$',
            'configure': lambda self, target: self.parse_statsd_timer(target)
        },
        {
            'match': '^stats_counts\.(?P<server>[^\.]+)\.(?P<swift_type>object)-server\.?(?P<http_method>[^\.]*)\.(?P<what>async_pendings|errors|timeouts)$',
            'target_type': 'count'
        },
        {
            'match': '^stats\.(?P<server>[^\.]+)\.(?P<swift_type>object)-server\.?(?P<http_method>[^\.]*)\.(?P<what>async_pendings|errors|timeouts)$',
            'target_type': 'rate'
        }
    ]

# vim: ts=4 et sw=4:
