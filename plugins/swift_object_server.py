from . import Plugin


class SwiftObjectServerPlugin(Plugin):

    targets = [
        {
            'match': '^stats\.timers\.(?P<server>[^\.]+)\.object-server\.(?P<http_method>[^\.]+)\.timing\.(?P<type>[^\.]+)$',
            'default_group_by': 'server',
            'default_graph_options': {'vtitle': 'duration in ms'},
            'target_type': 'timer'
        },
        {
            'match': '^stats_counts\.(?P<server>[^\.]+)\.object-server\.?(?P<http_method>[^\.]*)\.(?P<type>async_pendings|errors|timeouts)$',
            'default_group_by': 'server',
            'default_graph_options': {'vtitle': 'events seen in flushInterval'},
            'target_type': 'count'
        },
        {
            'match': '^stats\.(?P<server>[^\.]+)\.object-server\.?(?P<http_method>[^\.]*)\.(?P<type>async_pendings|errors|timeouts)$',
            'default_group_by': 'server',
            'default_graph_options': {'vtitle': 'events/s'},
            'target_type': 'rate'
        }
    ]

    def default_configure_target(self, match, target):
        m = target['tags'].get('http_method', '')
        t = target['tags']['type']
        color = None
        if m == 'GET'       and t in ('lower'   , 'timeouts'): color = self.colors['blue'][0]
        if m == 'GET'       and t in ('upper_90', 'errors')  : color = self.colors['blue'][1]
        if m == 'HEAD'      and t in ('lower'   , 'timeouts'): color = self.colors['yellow'][0]
        if m == 'HEAD'      and t in ('upper_90', 'errors')  : color = self.colors['yellow'][1]
        if m == 'PUT'       and t in ('lower'   , 'timeouts'): color = self.colors['green'][0]
        if m == 'PUT'       and t in ('upper_90', 'errors')  : color = self.colors['green'][1]
        if m == 'REPLICATE' and t in ('lower'   , 'timeouts'): color = self.colors['brown'][0]
        if m == 'REPLICATE' and t in ('upper_90', 'errors')  : color = self.colors['brown'][1]
        if m == 'DELETE'    and t in ('lower'   , 'timeouts'): color = self.colors['red'][0]
        if m == 'DELETE'    and t in ('upper_90', 'errors')  : color = self.colors['red'][1]
        if t == 'async_pendings': color = self.colors['turq'][0]
        # maybe better just a config function that gets called when the graph is done. that way we don't config any things that will be filteredout,
        # and also, we can change config based on the entire graph. maybe a graph_config_fn attrib per target_type which gets called for each target_type in a graph
        if color is not None:
            return {'color': color}
        return {}

# vim: ts=4 et sw=4:
