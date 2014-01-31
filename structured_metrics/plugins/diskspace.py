from . import Plugin


class DiskspacePlugin(Plugin):
    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.diskspace\.(?P<mountpoint>[^\.]+)\.(?P<wwt>.*)$',
            'target_type': 'gauge',
        }
    ]

    def sanitize(self, target):
        (u, mtype) = target['tags']['wwt'].split('_')
        units = {
            'byte': 'B',
            'inodes': 'Ino'
        }
        target['tags']['unit'] = units[u]
        target['tags']['type'] = mtype
        del target['tags']['wwt']

# vim: ts=4 et sw=4:
