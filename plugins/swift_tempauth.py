from . import Plugin


class SwiftTempauthPlugin(Plugin):
    targets = [
        {
            'match': '^stats\.(?P<server>[^\.]+)\.tempauth\.AUTH_\.(?P<type>[^\.]+)$',
            'default_graph_options': {'vtitle': 'events/s'},
            'target_type': 'rate'
        },
        {
            'match': '^stats_counts\.(?P<server>[^\.]+)\.tempauth\.AUTH_\.(?P<type>[^\.]+)$',
            'default_graph_options': {'vtitle': 'events seen in flushInterval'},
            'target_type': 'count'
        }
    ]

# vim: ts=4 et sw=4:
