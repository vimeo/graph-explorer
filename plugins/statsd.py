from . import Plugin


class StatsdPlugin(Plugin):
    '''
    'use this in combination with: derivative(statsd.*.udp_packet_receive_errors)',
    '''
    target_types = {
        'count': {
            'match': 'statsd\.(?P<type>numStats)',
            'default_graph_options': {'vtitle': 'stats (metrics) seen in interval'}
        },
        'timer_count': {
            'match': [
                #'^stats\.(?P<server>timers)\.(?P<timer>.*)\.count$',
                '^stats\.(?P<server>statsd)\.(?P<type>[^\.]+)$',  # packets_received, bad_lines_seen
                '^stats\.(?P<server>statsd)\.(?P<type>graphiteStats\.calculationtime)$',
                '^statsd\.(?P<type>numStats)$'
            ],
            'default_graph_options': {'vtitle': 'packets received per timer metric in interval'}
        },
        'counter': {
            'match': 'stats\.statsd\.(?P<type>graphiteStats\.last_[^\.]+)$',  # last_flush, last_exception. number of seconds since.
        },
        'rate': {
            'match': 'stats\.statsd\.(?P<type>graphiteStats\.last_[^\.]+)$',  # last_flush, last_exception. number of seconds since.
        }
    }
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

    def generate_targets(self, target_type, match):
        tags = match.groupdict()
        tags.update({'target_type': target_type, 'plugin': self.classname_to_tag()})
        t = match.string
        if target_type is 'rate':
            t = 'derivative(%s)' % t
        target = {
            'target': t,
            'tags': tags
        }
        target = self.configure_target(target)
        return {self.get_target_id(target): target}

# vim: ts=4 et sw=4:
