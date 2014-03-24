from . import Plugin


class VmstatPlugin(Plugin):
    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.vmstat\.(?P<type>.*)$',
            'target_type': 'rate',
            'tags': {'unit': 'Page'}
        }
    ]

    def sanitize(self, target):
        target['tags']['type'] = target['tags']['type'].replace('pgpg', 'paging_')
        target['tags']['type'] = target['tags']['type'].replace('pswp', 'swap_')
# vim: ts=4 et sw=4:
