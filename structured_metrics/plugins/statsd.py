from . import Plugin


class StatsdPlugin(Plugin):
    '''
    'use this in combination with: derivative(statsd.*.udp_packet_receive_errors)',
    '''
    targets = [
        {
            'match': 'statsd\.(?P<wtt>numStats)',
            'target_type': 'count'
        },
        {
            'match': [
                #'^stats\.(?P<server>timers)\.(?P<timer>.*)\.count$',
                '^stats\.(?P<server>statsd)\.(?P<wtt>[^\.]+)$',  # packets_received, bad_lines_seen
            ],
            'target_type': 'count'
        },
        {
            'match': '^stats\.(?P<server>statsd)\.(?P<wtt>graphiteStats\.calculationtime)$',
            'target_type': 'gauge',
        },
        {
            'match': 'stats\.statsd\.(?P<wtt>graphiteStats\.last_[^\.]+)$',  # last_flush, last_exception. number of seconds since.
            'targets': [
                {
                    'target_type': 'counter'
                },
                {
                    'target_type': 'rate',
                    'configure': lambda self, target: {'target': 'derivative(%s)' % target['target']}
                },
                # this requires:
                # https://github.com/graphite-project/graphite-web/pull/133
                # https://github.com/graphite-project/graphite-web/pull/135/
                # the keepLastValue is a workaround for https://github.com/graphite-project/graphite-web/pull/91
                {
                    'target_type': 'gauge',
                    'configure': lambda self, target: {'target': 'diffSeries(identity("a"),keepLastValue(%s))' % target['target']}
                }
            ]
        }
    ]
    # example graph definition. (can be seen by querying for eg.
    # 'statsd_graph').  not very useful right now. want to explore this
    # further..
    graphs = {
        'statsd_graph': {
            'match': '^stats.statsd.packets_received$',
            'graph': {
                'targets': [
                    'stats.statsd.packets_received',
                    'stats.statsd.bad_lines_seen',
                    'stats.statsd.graphiteStats.calculationtime',
                    'derivative(stats.statsd.graphiteStats.last_flush)',
                    'derivative(stats.statsd.graphiteStats.last_exception)',
                    'statsd.numStats'
                ]
            }
        }
    }

    def sanitize(self, target):
        if target['tags']['wtt'] == 'packets_received':
            target['tags']['what'] = 'packets'
            target['tags']['type'] = 'received'
        if target['tags']['wtt'] == 'bad_lines_seen':
            target['tags']['what'] = 'statsd_lines'
            target['tags']['type'] = 'received_bad'
        if target['tags']['wtt'] == 'numStats':
            target['tags']['what'] = 'stats'
            target['tags']['type'] = 'sent'
        if target['tags']['wtt'] == 'graphiteStats.calculationtime':
            target['tags']['what'] = 'seconds'
            target['tags']['type'] = 'calculationtime'
        if target['tags']['wtt'] == 'graphiteStats.last_flush':
            target['tags']['what'] = 'timestamp'
            target['tags']['type'] = 'last_flush'
        if target['tags']['wtt'] == 'graphiteStats.last_exception':
            target['tags']['what'] = 'timestamp'
            target['tags']['type'] = 'last_exception'
        del target['tags']['wtt']
# vim: ts=4 et sw=4:
