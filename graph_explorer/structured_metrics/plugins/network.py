from . import Plugin


class NetworkPlugin(Plugin):
    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.network\.(?P<device>[^\.]+)\.(?P<wt>.*)$',
            'target_type': 'rate',
        }
    ]

    def sanitize(self, target):
        if target['tags']['wt'].endswith('_bit'):
            target['tags']['unit'] = 'B/s'
            target['tags']['type'] = target['tags']['wt'].split('_')[0]
        elif target['tags']['wt'].endswith('_errors'):
            target['tags']['unit'] = 'Err/s'
            target['tags']['type'] = target['tags']['wt'].split('_')[0]
        else:
            target['tags']['unit'] = 'Pckt/s'
            target['tags']['type'] = target['tags']['wt']
        del target['tags']['wt']

# vim: ts=4 et sw=4:
