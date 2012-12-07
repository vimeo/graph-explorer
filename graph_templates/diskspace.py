from . import GraphTemplate
class DiskspaceTemplate(GraphTemplate):
    pattern_graph = "^servers\.([^\.]+)\.diskspace\.root\.gigabyte_avail$"
    target_types = {
        'diskspace_count': { 
            'match': '^servers\.(?P<server>[^\.]+)\.diskspace\.(?P<mountpoint>[^\.]+)\.(?P<type>.*)$',
            'default_group_by': 'server',
            'default_graph_options': {'state': 'stacked', 'vtitle': 'space'}
        }
    }

    def configure_target (self, target):
        mount = target['tags']['mountpoint']
        color_assign = {
            '_var': self.colors['red'][0],
            '_lib': self.colors['orange'][1],
            '_boot': self.colors['blue'][0],
            '_tmp': self.colors['purple'][0],
            '_root': self.colors['green'][0]
        }
        if mount in color_assign:
            target['color'] = color_assign[mount]

        return target

    def generate_graphs(self, match):
        return {}

# vim: ts=4 et sw=4:
