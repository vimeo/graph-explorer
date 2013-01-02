from . import Plugin


class NetworkPlugin(Plugin):
    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.network\.(?P<device>[^\.]+)\.(?P<type>.*)$',
            'default_group_by': 'server',
            'target_type': 'gauge'
        }
    ]
# vim: ts=4 et sw=4:
