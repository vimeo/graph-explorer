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
            'tags': {'unit': 'Req/s'}
        },
        {
            'match': '^stats_counts\.(?P<server>[^\.]+)\.(?P<service>tempauth)\.AUTH_\.(?P<type>[^\.]+)$',
            'target_type': 'count',
            'tags': {'unit': 'Req'}
        },
        # object-server
        {
            'match': '^stats\.timers\.(?P<server>[^\.]+)\.(?P<service>object-server)\.(?P<http_method>[^\.]+)\.timing\.(?P<tosplit>[^\.]+)$',
            'tags': {'swift_type': 'object'},
            'configure': lambda self, target: self.parse_statsd_timer(target),
        },
        {
            'match': '^stats_counts\.(?P<server>[^\.]+)\.(?P<service>object-server)\.?(?P<http_method>[^\.]*)\.(?P<unit>async_pendings|errors|timeouts)$',
            'target_type': 'count',
            'tags': {'swift_type': 'object'}
        },
        {
            'match': '^stats\.(?P<server>[^\.]+)\.(?P<service>object-server)\.?(?P<http_method>[^\.]*)\.(?P<unit>async_pendings|errors|timeouts)$',
            'target_type': 'rate',
            'tags': {'swift_type': 'object'}
        },
        # object-auditor
        {
            'match': '^stats\.timers\.(?P<server>[^\.]+)\.(?P<service>object-auditor)\.(?P<http_method>[^\.]+)\.timing\.(?P<tosplit>[^\.]+)$',
            'configure': lambda self, target: self.parse_statsd_timer(target)
        },
        # misc
        {
            'match': '^stats\.(?P<server>[^\.]+)\.(?P<service>[^\.]+)\.failures$',
            'target_type': 'rate',
            'tags': {'unit': 'Err/s'}
        }
    ]

    def sanitize(self, target):
        if 'wt' not in target['tags']:
            return
        sanitizer = {
            'xfer': ('B', 'transferred'),
            'errors': ('Err', None),
            'handoff_count': ('handoffs', 'node'),
            'handoff_all_count': ('handoffs', 'only hand-off locations'),
            'client_disconnects': ('disconnects', 'client'),
            'client_timeouts': ('timeouts', 'client')
        }
        wt = target['tags']['wt']
        target['tags']['unit'] = sanitizer[wt][0]
        if sanitizer[wt][1] is not None:
            target['tags']['type'] = sanitizer[wt][1]
        del target['tags']['wt']

# vim: ts=4 et sw=4:
