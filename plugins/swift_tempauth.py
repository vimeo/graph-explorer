from . import Plugin


class SwiftTempauthPlugin(Plugin):
    targets = [
        {
            'match': '^stats\.(?P<server>[^\.]+)\.tempauth\.AUTH_\.(?P<type>[^\.]+)$',
            'target_type': 'rate'
        },
        {
            'match': '^stats_counts\.(?P<server>[^\.]+)\.tempauth\.AUTH_\.(?P<type>[^\.]+)$',
            'target_type': 'count'
        }
    ]

# vim: ts=4 et sw=4:
