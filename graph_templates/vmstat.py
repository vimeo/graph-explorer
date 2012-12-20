from . import GraphTemplate


class VmstatTemplate(GraphTemplate):
    target_types = {
        'rate': {
            'match': '^servers\.(?P<server>[^\.]+)\.vmstat\.(?P<type>.*)$',
            'default_group_by': 'server',
            'default_graph_options': {'vtitle': 'per second'}
        }
    }

# vim: ts=4 et sw=4:
