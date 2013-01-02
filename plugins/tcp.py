from . import Plugin


class TcpPlugin(Plugin):
    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.(?P<protocol>tcp)\.(?P<type>.*)$',
            'default_group_by': 'server',
            'default_graph_options': {'vtitle': 'per second'},
            'target_type': 'rate'
        }
    ]

# vim: ts=4 et sw=4:
