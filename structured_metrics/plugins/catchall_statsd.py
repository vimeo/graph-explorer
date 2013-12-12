from . import Plugin


class CatchallStatsdPlugin(Plugin):
    """
    Like catchall, but for targets from statsd (presumably)
    """
    priority = -4

    targets = [
        {
            'match': '^stats\.gauges\.(?P<tosplit>.*)',
            'target_type': 'gauge',
            'configure': [
                lambda self, target: self.add_tag(target, 'unit', 'unknown'),
                lambda self, target: self.add_tag(target, 'source', 'statsd'),
                lambda self, target: self.autosplit(target)
            ]
        },
        {
            'match': '^stats\.timers\.(?P<tosplit>.*)',
            'target_type': 'gauge',
            'configure': lambda self, target: self.parse_timer(target)
        },
        {
            'match': '^stats\.(?P<tosplit>.*)',
            'target_type': 'rate',
            'configure': [
                lambda self, target: self.add_tag(target, 'unit', 'unknown/s'),
                lambda self, target: self.add_tag(target, 'source', 'statsd'),
                lambda self, target: self.autosplit(target)
            ]
        },
        {
            'match': '^stats_counts\.(?P<tosplit>.*)',
            'target_type': 'count',
            'configure': [
                lambda self, target: self.add_tag(target, 'unit', 'unknown'),
                lambda self, target: self.add_tag(target, 'source', 'statsd'),
                lambda self, target: self.autosplit(target)
            ]
        },
    ]

    def parse_timer(self, target):
        # see if we can get info from the end of the metric string
        nodes = target['tags']['tosplit'].split('.')
        target['tags']['target_type'] = 'gauge'
        if len(nodes) > 2 and nodes[-1].startswith('bin_') and nodes[-2] == 'histogram':
            # graphite uses '.' as node delimiters, so decimal numbers use '_' instead of '.'
            target['tags']['bin_upper'] = nodes[-1].replace('bin_', '').replace('_', '.', 1)
            target['tags']['unit'] = 'freq_abs'
            target['tags']['orig_unit'] = 'ms'
            nodes = nodes[:-2]
        # this is a workaround for buggy metric names like "stats.timers.foo.bar.histogram.bin_0.5"
        # i.e. where the decimal '.' is not replaced by a '_'
        elif len(nodes) > 3 and nodes[-2].startswith('bin_') and nodes[-3] == 'histogram':
            target['tags']['bin_upper'] = "%s.%s" % (nodes[-2].replace('bin_', ''), nodes[-1])
            target['tags']['unit'] = 'freq_abs'
            target['tags']['orig_unit'] = 'ms'
            nodes = nodes[:-3]
        elif len(nodes) > 1:
            if nodes[-1] in ('lower', 'mean', 'mean_90', 'median', 'std', 'sum', 'sum_90', 'upper', 'upper_90'):
                target['tags']['type'] = nodes[-1]
                target['tags']['unit'] = 'ms'
                nodes = nodes[:-1]
            elif nodes[-1] == 'count_ps':
                target['tags']['target_type'] = 'rate'
                target['tags']['unit'] = 'Pckt/s'
                nodes = nodes[:-1]
            elif nodes[-1] == 'count':
                target['tags']['target_type'] = 'count'
                target['tags']['unit'] = 'Pckt'
                nodes = nodes[:-1]
        self.autosplit(target, nodes=nodes)

        target['tags']['source'] = 'statsd'

# vim: ts=4 et sw=4:
