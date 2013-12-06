from . import Plugin


class SwiftTempauthPlugin(Plugin):
    targets = [
        {
            'match': '^stats\.(?P<server>[^\.]+)\.tempauth\.AUTH_\.(?P<type>[^\.]+)$',
            'target_type': 'rate',
            'configure': lambda self, target: self.add_tag(target, 'what', 'requests')
        },
        {
            'match': '^stats_counts\.(?P<server>[^\.]+)\.tempauth\.AUTH_\.(?P<type>[^\.]+)$',
            'target_type': 'count',
            'configure': lambda self, target: self.add_tag(target, 'what', 'requests')
        }
    ]

# vim: ts=4 et sw=4:
