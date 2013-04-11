from . import Plugin

class CarbonPlugin(Plugin):
    '''
    these definitions are probably not correct and need to be adjusted.
    a lot of these might actually be rates and/or in different units. somebody fixme kthx!
    '''
    targets = [
        {
            'match': 'carbon\.agents\.(?P<agent>[^\.]+)\.(?P<wtt>[^\.]+)',
            'target_type': 'gauge'
        },
        {
            'match': 'carbon\.agents\.(?P<agent>[^\.]+)\.cache\.(?P<wtt>[^\.]+)',
            'target_type': 'gauge'
        },
    ]

    def sanitize(self, target):
        if target['tags']['wtt'] == 'avgUpdateTime':
            target['tags']['what'] = 'ms'
            target['tags']['type'] = 'update_time'
        if target['tags']['wtt'] == 'committedPoints':
            target['tags']['what'] = 'datapoints'
            target['tags']['type'] = 'committed'
        if target['tags']['wtt'] == 'cpuUsage':
            target['tags']['what'] = 'jiffies'
            target['tags']['type'] = 'carbon_cpu_user'
        if target['tags']['wtt'] == 'creates':
            target['tags']['what'] = 'whisper_files'
            target['tags']['type'] = 'created'
        if target['tags']['wtt'] == 'errors':
            target['tags']['what'] = 'errors'
            target['tags']['type'] = 'carbon'
        if target['tags']['wtt'] == 'memUsage':
            target['tags']['what'] = 'bytes'
            target['tags']['type'] = 'carbon_mem'
        if target['tags']['wtt'] == 'metricsReceived':
            target['tags']['what'] = 'metrics'
            target['tags']['type'] = 'received'
        if target['tags']['wtt'] == 'pointsPerUpdate':
            target['tags']['what'] = 'datapoints_per_update'
        if target['tags']['wtt'] == 'updateOperations':
            target['tags']['what'] = 'updates'
        if target['tags']['wtt'] == 'overflow':
            target['tags']['what'] = 'overflows'
        if target['tags']['wtt'] == 'queries':
            target['tags']['what'] = 'queries'
        if target['tags']['wtt'] == 'queues':
            target['tags']['what'] = 'queues'
        if target['tags']['wtt'] == 'size':
            target['tags']['what'] = 'bytes'
            target['tags']['type'] = 'cache_size'
        del target['tags']['wtt']
# vim: ts=4 et sw=4:
