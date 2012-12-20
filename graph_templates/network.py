from . import GraphTemplate


class NetworkTemplate(GraphTemplate):
    target_types = {
        'gauge': {
            'match': '^servers\.(?P<server>[^\.]+)\.network\.(?P<device>[^\.]+)\.(?P<type>.*)$',
            'default_group_by': 'server',
        }
    }
# vim: ts=4 et sw=4:
