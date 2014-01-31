from . import Plugin


class DiamondOpenstackSwiftPlugin(Plugin):

    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.openstackswift\.(?P<category>container_metrics)\.(?P<account>[^\.]+)\.(?P<container>[^\.]+)\.(?P<wt>[^\.]+)$',
            'target_type': 'gauge',
        },
        {
            'match': '^servers\.(?P<server>[^\.]+)\.openstackswift\.(?P<category>dispersion)\.(?P<what>container|object|errors)\.?(?P<wt>[^\.]*)$',
            'target_type': 'gauge',
        }
    ]

    def sanitize(self, target):
        if target['tags'].get('what', '') == 'container':
            target['tags']['what'] = 'containers'
        if target['tags'].get('what', '') == 'object':
            target['tags']['what'] = 'objects'

        if 'wt' in target['tags']:
            if target['tags']['wt'] == 'bytes':
                target['tags']['unit'] = 'B'
                target['tags']['type'] = 'used'
            if target['tags']['wt'] == 'objects':
                target['tags']['what'] = 'objects'
                target['tags']['type'] = 'present'
            if target['tags']['wt'] == 'x_timestamp':
                target['tags']['what'] = 'timestamp'
                target['tags']['type'] = 'x'
            if target['tags']['wt'] == 'copies_found':
                target['tags']['type'] = 'found'
            if target['tags']['wt'] == 'copies_expected':
                target['tags']['type'] = 'expected'
            if target['tags']['wt'] == 'pct_found':
                target['tags']['type'] = 'found'
                target['tags']['target_type'] = target['tags']['target_type'] + '_pct'
            if target['tags']['wt'] == 'retries':
                target['tags']['type'] = 'retries_query_' + target['tags']['what']
                target['tags']['what'] = 'events'
            if target['tags']['wt'].startswith('missing_') or target['tags']['wt'] == 'overlapping':  # this should be the rest:
                target['tags']['type'] = target['tags']['wt']
            del target['tags']['wt']


# vim: ts=4 et sw=4:
