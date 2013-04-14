from . import Plugin


class SwiftObjectServerPlugin(Plugin):

    targets = [
        {
            'match': '^stats\.timers\.(?P<server>[^\.]+)\.object-server\.(?P<http_method>[^\.]+)\.timing\.(?P<what>[^\.]+)$',
            'target_type': 'timer'
        },
        {
            'match': '^stats_counts\.(?P<server>[^\.]+)\.object-server\.?(?P<http_method>[^\.]*)\.(?P<what>async_pendings|errors|timeouts)$',
            'target_type': 'count'
        },
        {
            'match': '^stats\.(?P<server>[^\.]+)\.object-server\.?(?P<http_method>[^\.]*)\.(?P<what>async_pendings|errors|timeouts)$',
            'target_type': 'rate'
        }
    ]

# vim: ts=4 et sw=4:
