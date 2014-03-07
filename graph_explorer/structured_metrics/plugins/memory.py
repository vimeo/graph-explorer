from . import Plugin


class MemoryPlugin(Plugin):
    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.memory\.(?P<type>.*)$',
            'target_type': 'gauge',
            'tags': {
                'unit': 'B',
                'where': 'system_memory'
            },
            'configure': lambda self, target: self.fix_underscores(target, 'type'),
        }
    ]

    def sanitize(self, target):
        target['tags']['type'] = target['tags']['type'].replace('mem_', 'ram_')

# vim: ts=4 et sw=4:
