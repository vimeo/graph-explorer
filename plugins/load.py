from . import Plugin


class LoadPlugin(Plugin):
    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.loadavg\.(?P<wt>.*)$',
            'target_type': 'gauge'
        }
    ]

    def default_configure_target(self, target):
        # add extra light version..
        red = ('#FFA791', self.colors['red'][0], self.colors['red'][1])
        t = target['tags']['type']
        color_assign = {'01': 2, '05': 1, '15': 0}
        if t in color_assign.keys():
            target['color'] = red[color_assign[t]]
        return target

    def sanitize(self, target):
        if target['tags']['wt'] in ('01','05','15'):
            target['tags']['what'] = 'load'
            target['tags']['type'] = target['tags']['wt']
        if target['tags']['wt'] in ('processes_running', 'processes_total'):  # this should be ev. else
            (target['tags']['what'], target['tags']['type']) = target['tags']['wt'].split('_')
        del target['tags']['wt']
# vim: ts=4 et sw=4:
