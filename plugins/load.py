from . import Plugin


class LoadPlugin(Plugin):
    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.loadavg\.(?P<type>.*)$',
            'default_group_by': 'server',
            'default_graph_options': {'state': 'stacked'},
            'target_type': 'count'
        }
    ]

    def default_configure_target(self, match, target):
        # add extra light version..
        red = ('#FFA791', self.colors['red'][0], self.colors['red'][1])
        t = target['tags']['type']
        color_assign = {'01': 2, '05': 1, '15': 0}
        if t in color_assign.keys():
            target['color'] = red[color_assign[t]]
        return target

# vim: ts=4 et sw=4:
