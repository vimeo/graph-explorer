from . import GraphTemplate


class FilestatTemplate(GraphTemplate):

    target_types = {
        'gauge': {
            'match': '^servers\.(?P<server>[^\.]+)\.files\.(?P<type>.*)$',
            'default_group_by': 'server',
        },
    }

# vim: ts=4 et sw=4:
