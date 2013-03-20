from . import Plugin


class DiskspacePlugin(Plugin):
    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.diskspace\.(?P<mountpoint>[^\.]+)\.(?P<wwt>.*)$',
            'targets': [
                {
                    'target_type': 'gauge',
                    'configure': lambda self, target: self.configure_color(target)
                },
                {
                    'target_type': 'rate',
                    'configure': [
                        lambda self, target: {'target': 'movingAverage(derivative(%s),60)' % target['target']},
                        lambda self, target: self.configure_color(target)
                    ]
                }
            ]
        }
    ]

    def configure_color(self, target):
        mount = target['tags']['mountpoint']
        color_assign = {
            '_var': self.colors['red'][0],
            '_lib': self.colors['orange'][1],
            '_boot': self.colors['blue'][0],
            '_tmp': self.colors['purple'][0],
            '_root': self.colors['green'][0]
        }
        if mount in color_assign:
            return {'color': color_assign[mount]}
        return {}

    def sanitize(self, target):
        (what, type) = target['tags']['wwt'].split('_')
        if what == 'byte':
            what = 'bytes'
        target['tags']['what'] = what
        target['tags']['type'] = type
        del target['tags']['wwt']

# vim: ts=4 et sw=4:
