from . import GraphTemplate

class SwiftObjectServerTemplate(GraphTemplate):

    #class_tag = 'swift_object_server'
    pattern_graph = "^stats.timers\.([^\.]+)\.object-server\.GET.timing.lower$"
    target_types = {
        'swift_object_server_timer': {
            'match': '^stats\.timers\.(?P<server>[^\.]+)\.object-server\.(?P<http_method>[^\.]+)\.timing\.(?P<type>[^\.]+)$',
            'default_group_by': 'server',
            'default_graph_options': {'vtitle': 'duration in ms'}
        },
        'swift_object_server_count': {
            'match': '^stats_counts\.(?P<server>[^\.]+)\.object-server\.?(?P<http_method>[^\.]*)\.(?P<type>async_pendings|errors|timeouts)$',
            'default_group_by': 'server',
            'default_graph_options': {'vtitle': 'events seen in flushInterval'}
        },
        'swift_object_server_rate': {
            'match': '^stats\.(?P<server>[^\.]+)\.object-server\.?(?P<http_method>[^\.]*)\.(?P<type>async_pendings|errors|timeouts)$',
            'default_group_by': 'server',
            'default_graph_options': {'vtitle': 'events/s'}
        }
    }

    def configure_target(self, target):
        m = target['tags'].get('http_method','')
        t = target['tags']['type']
        if m == 'GET'       and t in ('lower'   , 'timeouts'): target['color'] = self.colors['blue'][0]
        if m == 'GET'       and t in ('upper_90', 'errors')  : target['color'] = self.colors['blue'][1]
        if m == 'HEAD'      and t in ('lower'   , 'timeouts'): target['color'] = self.colors['yellow'][0]
        if m == 'HEAD'      and t in ('upper_90', 'errors')  : target['color'] = self.colors['yellow'][1]
        if m == 'PUT'       and t in ('lower'   , 'timeouts'): target['color'] = self.colors['green'][0]
        if m == 'PUT'       and t in ('upper_90', 'errors')  : target['color'] = self.colors['green'][1]
        if m == 'REPLICATE' and t in ('lower'   , 'timeouts'): target['color'] = self.colors['brown'][0]
        if m == 'REPLICATE' and t in ('upper_90', 'errors')  : target['color'] = self.colors['brown'][1]
        if m == 'DELETE'    and t in ('lower'   , 'timeouts'): target['color'] = self.colors['red'][0]
        if m == 'DELETE'    and t in ('upper_90', 'errors')  : target['color'] = self.colors['red'][1]
        if t == 'async_pendings': target['color'] = self.colors['turq'][0]
        # maybe better just a config function that gets called when the graph is done. that way we don't config any things that will be filteredout,
        # and also, we can change config based on the entire graph. maybe a graph_config_fn attrib per target_type which gets called for each target_type in a graph
        return target

    def generate_graphs(self, match):
        return {} # no longer needed. soon i hope. see above

# vim: ts=4 et sw=4:
