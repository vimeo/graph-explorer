from . import Plugin


class CarbonPlugin(Plugin):
    '''
    these definitions are probably not correct and need to be adjusted.
    a lot of these might actually be rates and/or in different units. somebody fixme kthx!
    '''
    targets = [
        {
            'match': 'carbon\.agents\.(?P<agent>[^\.]+)\.(?P<wtt>[^\.]+)$',
            'target_type': 'gauge'
        },
        {
            'match': 'carbon\.agents\.(?P<agent>[^\.]+)\.cache\.(?P<wtt>[^\.]+)$',
            'target_type': 'gauge'
        },
    ]

    def sanitize(self, target):
        if target['tags']['wtt'] == 'avgUpdateTime':
            target['tags']['unit'] = 'ms'
            target['tags']['type'] = 'update_time'
        if target['tags']['wtt'] == 'committedPoints':
            target['tags']['unit'] = 'datapoints'
            target['tags']['type'] = 'committed'
        if target['tags']['wtt'] == 'cpuUsage':
            target['tags']['unit'] = 'jiffies'
            target['tags']['type'] = 'carbon_cpu_user'
        if target['tags']['wtt'] == 'creates':
            target['tags']['unit'] = 'whisper_files'
            target['tags']['type'] = 'created'
        if target['tags']['wtt'] == 'errors':
            target['tags']['unit'] = 'Err'
            target['tags']['type'] = 'carbon'
        if target['tags']['wtt'] == 'memUsage':
            target['tags']['unit'] = 'B'
            target['tags']['type'] = 'carbon_mem'
        if target['tags']['wtt'] == 'metricsReceived':
            target['tags']['unit'] = 'metrics'
            target['tags']['type'] = 'received'
        if target['tags']['wtt'] == 'pointsPerUpdate':
            target['tags']['unit'] = 'datapoints_per_update'
        if target['tags']['wtt'] == 'updateOperations':
            target['tags']['unit'] = 'updates'
        if target['tags']['wtt'] == 'queries':
            target['tags']['unit'] = 'queries'
        if target['tags']['wtt'] == 'queues':
            target['tags']['unit'] = 'queues'
        if target['tags']['wtt'] == 'size':
            target['tags']['unit'] = 'B'
            target['tags']['type'] = 'cache_size'
        if target['tags']['wtt'] == 'overflow':
            target['tags']['unit'] = 'events'
            target['tags']['type'] = 'overflow'
        del target['tags']['wtt']
# vim: ts=4 et sw=4:
