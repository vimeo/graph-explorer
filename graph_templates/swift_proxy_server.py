from . import GraphTemplate


class SwiftProxyServerTemplate(GraphTemplate):
    http_methods = ['GET', 'HEAD', 'PUT', 'REPLICATE']
    target_types = {
        'timer': {
            'match': '^stats.timers\.(?P<server>[^\.]+)\.proxy-server\.(?P<swift_type>account|container|object)\.(?P<http_method>[^\.]+)\.(?P<http_code>[^\.]+)\.timing\.(?P<type>[^\.]+)$',
            'default_group_by': 'server',
            'default_graph_options': {'vtitle': 'duration in ms'}
        },
        'count': {
            'match': '^stats_counts\.(?P<server>[^\.]+)\.proxy-server\.?(?P<swift_type>account|container|object)?\.?(?P<http_method>[^\.]*)\.?(?P<http_code>[^\.]*)\.(?P<type>[^\.]+)$',
            'default_group_by': 'server',
            'default_graph_options': {'vtitle': 'events seen in flushInterval'}
        },
        'rate': {
            'match': '^stats\.(?P<server>[^\.]+)\.proxy-server\.?(?P<swift_type>account|container|object)?\.?(?P<http_method>[^\.]*)\.?(?P<http_code>[^\.]*)\.(?P<type>[^\.]+)$',
            'default_group_by': 'server',
            'default_graph_options': {'vtitle': 'events/s'}
        },
    }

    def generate_targets(self, target_type, match):
        tags = match.groupdict()
        tags.update({'target_type': target_type, 'template': self.classname_to_tag()})
        t = match.string
        # 'xfer' is transferred bytes..
        if tags['type'] == 'xfer':
            tags['type'] = 'xfer_bytes'
        target = {
            'target': t,
            'tags': tags
        }
        target = self.configure_target(target)
        return {self.get_target_id(target): target}

    def configure_target(self, target):
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
        return target

# vim: ts=4 et sw=4:
