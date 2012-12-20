from . import Plugin


class DiskspacePlugin(Plugin):
    target_types = {
        'count': {
            'match': '^servers\.(?P<server>[^\.]+)\.diskspace\.(?P<mountpoint>[^\.]+)\.(?P<type>.*)$',
            'default_group_by': 'server',
            'default_graph_options': {'state': 'stacked', 'vtitle': 'space'}
        },
        'rate': {
            'match': '^servers\.(?P<server>[^\.]+)\.diskspace\.(?P<mountpoint>[^\.]+)\.(?P<type>.*)$',
            'default_group_by': 'server',
            'default_graph_options': {'state': 'stacked', 'vtitle': 'space change per minute'}
        }
    }

    def configure_target(self, target):
        mount = target['tags']['mountpoint']
        color_assign = {
            '_var': self.colors['red'][0],
            '_lib': self.colors['orange'][1],
            '_boot': self.colors['blue'][0],
            '_tmp': self.colors['purple'][0],
            '_root': self.colors['green'][0]
        }
        if mount in color_assign:
            target['color'] = color_assign[mount]

        return target

    def generate_targets(self, target_type, match):
        tags = match.groupdict()
        tags.update({'target_type': target_type, 'plugin': self.classname_to_tag()})
        if target_type is 'count':
            t = match.string
        else:
            # try to show this in a useful way
            #t = 'derivative(movingAverage(%s,50))' % match.string  # -> still shows FS clenaups as huge downspikes. log() graphs aren't very clear
            #t = 'removeBelowValue(derivative(%s),-10000000)' % match.string  # graphite internal server error?
            #t = 'derivative(movingAverage(%s,50.0))' % match.string  # can still show spikes though.. wish i could do movingAverage(%s,50) or so but graphite barfs on that.
            #t = 'movingAverage(derivative(%s),500)' % match.string  # graphite changes this to 500.0 so graphitejs doesn't recognize it.. and with 500.0 graphite barfs
            t = 'derivative(%s)' % match.string
        target = {
            'target': t,
            'tags': tags
        }
        target = self.configure_target(target)
        return {self.get_target_id(target): target}

# vim: ts=4 et sw=4:
