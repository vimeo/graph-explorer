from . import Plugin


class UdpPlugin(Plugin):
    target_types = {
        'rate': {
            'match': '^servers\.(?P<server>[^\.]+)\.(?P<protocol>udp)\.(?P<type>.*)$',
            'default_group_by': 'server',
            'default_graph_options': {'vtitle': 'per second'}
        }
    }

# vim: ts=4 et sw=4:
