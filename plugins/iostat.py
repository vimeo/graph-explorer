from . import Plugin


class IostatPlugin(Plugin):
    '''
    corresponds to diamond diskusage plugin
    '''
    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.iostat\.(?P<device>[^\.]+)\.(?P<type>.*)$',
            'default_group_by': 'server',
            'default_graph_options': {'state': 'stacked'},
            'target_type': 'gauge',
        },
        {
            'match': '^servers\.(?P<server>[^\.]+)\.iostat\.(?P<device>[^\.]+)\.(?P<type>.*)_per_second$',
            'default_group_by': 'server',
            'default_graph_options': {'state': 'stacked', 'vtitle': 'events/s'},
            'target_type': 'rate'
        }
    ]

# vim: ts=4 et sw=4:
