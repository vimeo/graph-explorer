from . import Plugin


class SockstatPlugin(Plugin):
    target_types = {
        'gauge': {
            'match': '^servers\.(?P<server>[^\.]+)\.sockets\.(?P<protocol>tcp|udp)?_?(?P<type>[^\.]+)$',
            'default_group_by': 'server',
            'default_graph_options': {'vtitle': 'gauges'}
        }
    }

# vim: ts=4 et sw=4:
