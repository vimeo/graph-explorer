from . import Plugin


class SwiftProxyServerPlugin(Plugin):
    http_methods = ['GET', 'HEAD', 'PUT', 'REPLICATE']
    targets = [
        {
            'match': '^stats.timers\.(?P<server>[^\.]+)\.proxy-server\.(?P<swift_type>account|container|object)\.(?P<http_method>[^\.]+)\.(?P<http_code>[^\.]+)\.timing\.(?P<tosplit>[^\.]+)$',
            'configure': lambda self, target: self.parse_statsd_timer(target)
        },
        {
            'match': '^stats_counts\.(?P<server>[^\.]+)\.proxy-server\.?(?P<swift_type>account|container|object)?\.?(?P<http_method>[^\.]*)\.?(?P<http_code>[^\.]*)\.(?P<wt>[^\.]+)$',
            'target_type': 'count'
        },
        {
            'match': '^stats\.(?P<server>[^\.]+)\.proxy-server\.?(?P<swift_type>account|container|object)?\.?(?P<http_method>[^\.]*)\.?(?P<http_code>[^\.]*)\.(?P<wt>[^\.]+)$',
            'target_type': 'rate'
        },
    ]

    def sanitize(self, target):
        if 'wt' not in target['tags']:
            return
        sanitizer = {
            'xfer': ('bytes', 'transferred'),
            'errors': ('errors', None),
            'handoff_count': ('handoffs', 'node'),
            'handoff_all_count': ('handoffs', 'only hand-off locations'),
            'client_disconnects': ('disconnects', 'client'),
            'client_timeouts': ('timeouts', 'client')
        }
        wt = target['tags']['wt']
        target['tags']['what'] = sanitizer[wt][0]
        if sanitizer[wt][1] is not None:
            target['tags']['type'] = sanitizer[wt][1]
        del target['tags']['wt']

# vim: ts=4 et sw=4:
