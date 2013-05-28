from . import Plugin


class StatsdPlugin(Plugin):
    '''
    'use this in combination with: derivative(statsd.*.udp_packet_receive_errors)',
    assumes that if you use prefixStats, it's of the format statsd.<statsd_server> , adjust as needed.
    '''
    targets = [
        Plugin.gauge(  '^statsd\.?(?P<server>[^\.]*)\.(?P<wtt>numStats)'),
        Plugin.gauge(  '^stats\.statsd\.?(?P<server>[^\.]*)\.(?P<wtt>processing_time)$'),
        Plugin.counter('^stats\.statsd\.?(?P<server>[^\.]*)\.(?P<wtt>[^\.]+)$'),  # packets_received, bad_lines_seen
        Plugin.gauge(  '^stats\.statsd\.?(?P<server>[^\.]*)\.(?P<wtt>graphiteStats\.calculationtime)$'),
        Plugin.gauge(  '^stats\.statsd\.?(?P<server>[^\.]*)\.(?P<wtt>graphiteStats\.flush_[^\.]+)$'), # flush_length, flush_time
        {
            'match': 'stats\.statsd\.?(?P<server>[^\.]*)\.(?P<wtt>graphiteStats\.last_[^\.]+)$',  # last_flush, last_exception. unix timestamp
            'targets': [
                {
                    'target_type': 'counter'
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
        },
        {
            'match': '^stats\.timers',
            'limit': 1,
            'target_type': 'count',
            'configure': [
                lambda self, target: {'target': 'sumSeries(%s)' % ','.join(['stats.timers.%s.count' % infix for infix in ['*', '*.*', '*.*.*', '*.*.*.*', '*.*.*.*.*']])},
                lambda self, target: self.add_tag(target, 'what', 'packets'),
                lambda self, target: self.add_tag(target, 'type', 'received_timer'),
            ]
        }
    ]
    # example graph definition. (can be seen by querying for eg.
    # 'statsd_graph').  not very useful right now. want to explore this
    # further..
    graphs = {
        'statsd_graph_example_nothing_new_here': {
            'match': '^stats\.statsd',
            'limit': 1,
            'graph': {
                'targets': [
                    'stats.statsd.packets_received',
                    {
                        'name': 'timer packets received per flushinterval',
                        'target': 'sumSeries(%s)' % ','.join(['stats.timers.%s.count' % infix for infix in ['*', '*.*.*.*.*', '*.*.*.*', '*.*.*', '*.*']])
                    },
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
        if 'wtt' not in target['tags']:
            return
        if target['tags']['wtt'] == 'packets_received':
            target['tags']['what'] = 'packets'
            target['tags']['type'] = 'received'
        if target['tags']['wtt'] == 'bad_lines_seen':
            target['tags']['what'] = 'statsd_lines'
            target['tags']['type'] = 'received_bad'
        if target['tags']['wtt'] == 'numStats':
            target['tags']['what'] = 'stats'
            target['tags']['type'] = 'sent_to_graphite'
        if target['tags']['wtt'] == 'graphiteStats.calculationtime':
            target['tags']['what'] = 'ms'
            target['tags']['type'] = 'calculationtime'
        if target['tags']['wtt'] == 'graphiteStats.last_exception':
            if target['tags']['target_type'] == 'counter':
                target['tags']['what'] = 'timestamp'
                target['tags']['type'] = 'last_exception'
            else:  # gauge
                target['tags']['what'] = 'seconds'
                target['tags']['type'] = 'last_exception age'
        if target['tags']['wtt'] == 'graphiteStats.last_flush':
            if target['tags']['target_type'] == 'counter':
                target['tags']['what'] = 'timestamp'
                target['tags']['type'] = 'last_flush'
            else:  # gauge
                target['tags']['what'] = 'seconds'
                target['tags']['type'] = 'last_flush age'
        if target['tags']['wtt'] == 'graphiteStats.flush_length':
            target['tags']['what'] = 'bytes'
            target['tags']['type'] = 'flush_to_graphite'
        if target['tags']['wtt'] == 'graphiteStats.flush_time':
            target['tags']['what'] = 'ms'
            target['tags']['type'] = 'flush_to_graphite'
        if target['tags']['wtt'] == 'processing_time':
            target['tags']['what'] = 'ms'
            target['tags']['type'] = 'processing'
        del target['tags']['wtt']
# vim: ts=4 et sw=4:
