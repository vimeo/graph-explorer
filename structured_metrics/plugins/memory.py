from . import Plugin


class MemoryPlugin(Plugin):
    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.memory\.(?P<type>.*)$',
            'target_type': 'gauge',
            'configure': [
                lambda self, target: self.fix_underscores(target, 'type'),
                lambda self, target: self.add_tag(target, 'where', 'system_memory')
            ]
        }
    ]

    def sanitize(self, target):
        target['tags']['unit'] = 'B'
        target['tags']['type'] = target['tags']['type'].replace('mem_', 'ram_')

# vim: ts=4 et sw=4:
