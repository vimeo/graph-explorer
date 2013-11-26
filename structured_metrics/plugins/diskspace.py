from . import Plugin


class DiskspacePlugin(Plugin):
    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.diskspace\.(?P<mountpoint>[^\.]+)\.(?P<wwt>.*)$',
            'target_type': 'gauge',
        }
    ]

    def sanitize(self, target):
        (what, mtype) = target['tags']['wwt'].split('_')
        if what == 'byte':
            what = 'bytes'
        target['tags']['what'] = what
        target['tags']['type'] = mtype
        del target['tags']['wwt']

# vim: ts=4 et sw=4:
