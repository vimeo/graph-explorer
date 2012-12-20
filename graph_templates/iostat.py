from . import GraphTemplate


class IostatTemplate(GraphTemplate):
    '''
    corresponds to diamond diskusage plugin
    '''
    target_types = {
        'gauge': {
            'match': '^servers\.(?P<server>[^\.]+)\.iostat\.(?P<device>[^\.]+)\.(?P<type>.*)$',
            'default_group_by': 'server',
            'default_graph_options': {'state': 'stacked'}
        },
        'rate': {
            'match': '^servers\.(?P<server>[^\.]+)\.iostat\.(?P<device>[^\.]+)\.(?P<type>.*)_per_second$',
            'default_group_by': 'server',
            'default_graph_options': {'state': 'stacked', 'vtitle': 'events/s'}
        }
    }

# vim: ts=4 et sw=4:
