from . import Plugin


class SwiftProxyServerPlugin(Plugin):
    http_methods = ['GET', 'HEAD', 'PUT', 'REPLICATE']
    targets = [
        {
            'match': '^stats.timers\.(?P<server>[^\.]+)\.proxy-server\.(?P<swift_type>account|container|object)\.(?P<http_method>[^\.]+)\.(?P<http_code>[^\.]+)\.timing\.(?P<type>[^\.]+)$',
            'default_group_by': 'server',
            'default_graph_options': {'vtitle': 'duration in ms'},
            'target_type': 'timer'
        },
        {
            'match': '^stats_counts\.(?P<server>[^\.]+)\.proxy-server\.?(?P<swift_type>account|container|object)?\.?(?P<http_method>[^\.]*)\.?(?P<http_code>[^\.]*)\.(?P<type>[^\.]+)$',
            'default_group_by': 'server',
            'default_graph_options': {'vtitle': 'events seen in flushInterval'},
            'target_type': 'count'
        },
        {
            'match': '^stats\.(?P<server>[^\.]+)\.proxy-server\.?(?P<swift_type>account|container|object)?\.?(?P<http_method>[^\.]*)\.?(?P<http_code>[^\.]*)\.(?P<type>[^\.]+)$',
            'default_group_by': 'server',
            'default_graph_options': {'vtitle': 'events/s'},
            'target_type': 'rate'
        },
    ]

    def default_configure_target(self, match, target):
        m = target['tags'].get('http_method', '')
        t = target['tags']['type']
        if m == 'GET'       and t in ('lower', 'timeouts', 'xfer'): target['color'] = self.colors['blue'][0]
        if m == 'GET'       and t in ('upper_90', 'errors')       : target['color'] = self.colors['blue'][1]
        if m == 'HEAD'      and t in ('lower', 'timeouts', 'xfer'): target['color'] = self.colors['yellow'][0]
        if m == 'HEAD'      and t in ('upper_90', 'errors')       : target['color'] = self.colors['yellow'][1]
        if m == 'PUT'       and t in ('lower', 'timeouts', 'xfer'): target['color'] = self.colors['green'][0]
        if m == 'PUT'       and t in ('upper_90', 'errors')       : target['color'] = self.colors['green'][1]
        if m == 'REPLICATE' and t in ('lower', 'timeouts', 'xfer'): target['color'] = self.colors['brown'][0]
        if m == 'REPLICATE' and t in ('upper_90', 'errors')       : target['color'] = self.colors['brown'][1]
        if m == 'DELETE'    and t in ('lower', 'timeouts', 'xfer'): target['color'] = self.colors['red'][0]
        if m == 'DELETE'    and t in ('upper_90', 'errors')       : target['color'] = self.colors['red'][1]
        # 'xfer' is transferred bytes..
        if target['tags']['type'] == 'xfer':
            target['tags']['type'] = 'xfer_bytes'
        return target

# vim: ts=4 et sw=4:
