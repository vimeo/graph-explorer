from . import Plugin


class DiskspacePlugin(Plugin):
    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.diskspace\.(?P<mountpoint>[^\.]+)\.(?P<wwt>.*)$',
            'targets': [
                {
                    'target_type': 'gauge',
                },
                {
                    'target_type': 'rate',
                    'configure': lambda self, target: {'target': 'movingAverage(derivative(%s),60)' % target['target']},
                }
            ]
        }
    ]

    def sanitize(self, target):
        (what, type) = target['tags']['wwt'].split('_')
        if what == 'byte':
            what = 'bytes'
        target['tags']['what'] = what
        target['tags']['type'] = type
        del target['tags']['wwt']

# vim: ts=4 et sw=4:
