from . import Plugin


class OpenstackSwift(Plugin):
    http_methods = ['GET', 'HEAD', 'PUT', 'REPLICATE']
    targets = [
        # proxy-server
        {
            'match': '^stats.timers\.(?P<server>[^\.]+)\.(?P<service>proxy-server)\.(?P<swift_type>account|container|object)\.(?P<http_method>[^\.]+)\.(?P<http_code>[^\.]+)\.timing\.(?P<tosplit>[^\.]+)$',
            'configure': lambda self, target: self.parse_statsd_timer(target)
        },
        {
            'match': '^stats_counts\.(?P<server>[^\.]+)\.(?P<service>proxy-server)\.?(?P<swift_type>account|container|object)?\.?(?P<http_method>[^\.]*)\.?(?P<http_code>[^\.]*)\.(?P<wt>[^\.]+)$',
            'target_type': 'count'
        },
        {
            'match': '^stats\.(?P<server>[^\.]+)\.(?P<service>proxy-server)\.?(?P<swift_type>account|container|object)?\.?(?P<http_method>[^\.]*)\.?(?P<http_code>[^\.]*)\.(?P<wt>[^\.]+)$',
            'target_type': 'rate'
        },
        # tempauth
        {
            'match': '^stats\.(?P<server>[^\.]+)\.(?P<service>tempauth)\.AUTH_\.(?P<type>[^\.]+)$',
            'target_type': 'rate',
            'configure': lambda self, target: self.add_tag(target, 'unit', 'Req/s')
        },
        {
            'match': '^stats_counts\.(?P<server>[^\.]+)\.(?P<service>tempauth)\.AUTH_\.(?P<type>[^\.]+)$',
            'target_type': 'count',
            'configure': lambda self, target: self.add_tag(target, 'unit', 'Req')
        },
        # object-server
        {
            'match': '^stats\.timers\.(?P<server>[^\.]+)\.(?P<service>object-server)\.(?P<http_method>[^\.]+)\.timing\.(?P<tosplit>[^\.]+)$',
            'configure': [
                lambda self, target: self.parse_statsd_timer(target),
                lambda self, target: self.add_tag(target, 'swift_type', 'object')
            ]
        },
        {
            'match': '^stats_counts\.(?P<server>[^\.]+)\.(?P<service>object-server)\.?(?P<http_method>[^\.]*)\.(?P<what>async_pendings|errors|timeouts)$',
            'target_type': 'count',
            'configure': lambda self, target: self.add_tag(target, 'swift_type', 'object')
        },
        {
            'match': '^stats\.(?P<server>[^\.]+)\.(?P<service>object-server)\.?(?P<http_method>[^\.]*)\.(?P<what>async_pendings|errors|timeouts)$',
            'target_type': 'rate',
            'configure': lambda self, target: self.add_tag(target, 'swift_type', 'object')
        },
        # object-auditor
        {
            'match': '^stats\.timers\.(?P<server>[^\.]+)\.(?P<service>object-auditor)\.(?P<http_method>[^\.]+)\.timing\.(?P<tosplit>[^\.]+)$',
            'configure': lambda self, target: self.parse_statsd_timer(target)
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
