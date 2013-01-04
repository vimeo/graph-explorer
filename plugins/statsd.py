from . import Plugin


class StatsdPlugin(Plugin):
    '''
    'use this in combination with: derivative(statsd.*.udp_packet_receive_errors)',
    '''
    targets = [
        {
            'match': 'statsd\.(?P<type>numStats)',
            'default_graph_options': {'vtitle': 'stats (metrics) seen in interval'},
            'target_type': 'count'
        },
        {
            'match': [
                #'^stats\.(?P<server>timers)\.(?P<timer>.*)\.count$',
                '^stats\.(?P<server>statsd)\.(?P<type>[^\.]+)$',  # packets_received, bad_lines_seen
            ],
            'default_graph_options': {'vtitle': 'packets received per timer metric in interval'},
            'target_type': 'count'
        },
        {
            'match': '^stats\.(?P<server>statsd)\.(?P<type>graphiteStats\.calculationtime)$',
            'target_type': 'gauge',
            'default_graph_options': {'vtitle': 'seconds'}
        },
        {
            'match': 'stats\.statsd\.(?P<type>graphiteStats\.last_[^\.]+)$',  # last_flush, last_exception. number of seconds since.
            'targets': [
                {
                    'target_type': 'counter'
                },
                {
                    'target_type': 'rate',
                    'configure': lambda self, match, target: {'target': 'derivative(%s)' % match.string}
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

# vim: ts=4 et sw=4:
