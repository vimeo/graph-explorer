from . import Plugin


class NetworkPlugin(Plugin):
    target_types = {
        'gauge': {
            'match': '^servers\.(?P<server>[^\.]+)\.network\.(?P<device>[^\.]+)\.(?P<type>.*)$',
            'default_group_by': 'server',
        }
    }
# vim: ts=4 et sw=4:
