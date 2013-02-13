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
                    # try to show this in a useful way
                    # 'derivative(movingAverage(%s,50))' % match.string  # -> still shows FS clenaups as huge downspikes. log() graphs aren't very clear
                    # 'removeBelowValue(derivative(%s),-10000000)' % match.string  # graphite internal server error?
                    # 'derivative(movingAverage(%s,50.0))' % match.string  # can still show spikes though.. wish i could do movingAverage(%s,50) or so but graphite barfs on that.
                    # 'movingAverage(derivative(%s),500)' % match.string  # graphite changes this to 500.0 so tswidget doesn't recognize it.. and with 500.0 graphite barfs
                    'configure': [
                        lambda self, target: {'target': 'derivative(%s)' % target['target']},
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
