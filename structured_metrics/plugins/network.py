from . import Plugin


class NetworkPlugin(Plugin):
    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.network\.(?P<device>[^\.]+)\.(?P<wt>.*)$',
            'target_type': 'rate',
            'targets': [
                {
                    'configure': [
                        lambda self, target: {'target': 'scale(summarize(%s, "10minute"),0.1)' % target['target']},
                        lambda self, target: self.add_tag(target, 'angle', 'summary-10m')
                    ]
                },
                {
                },
                {
                    'configure': [
                        lambda self, target: {'target': 'cumulative(%s)' % target['target']},
                        lambda self, target: self.add_tag(target, 'angle', 'cumul')
                    ]
                }
            ]
        }
    ]

    def sanitize(self, target):
        if target['tags']['wt'].endswith('_bit'):
            target['tags']['what'] = 'bits'
            target['tags']['type'] = target['tags']['wt'].split('_')[0]
        elif target['tags']['wt'].endswith('_errors'):
            target['tags']['what'] = 'errors'
            target['tags']['type'] = target['tags']['wt'].split('_')[0]
        else:
            target['tags']['what'] = 'packets'
            target['tags']['type'] = target['tags']['wt']
        del target['tags']['wt']

# vim: ts=4 et sw=4:
