from . import Plugin

class CollectdPlugin(Plugin):
    collectd_types = {
        'if_octets': ('bytes', 'rate'),
        'if_errors': ('errors', 'rate'),
        'if_packets': ('pkts', 'rate'),
        'cpu': ('cpu', 'gauge_pct'),
        'cpufreq': ('hz', 'gauge'),
        'protocol_counter': ('pkts', 'rate'),
        'tcp_connections': ('connections', 'gauge'),
        'load': ('load', 'gauge'),
        'uptime': ('secs', 'gauge'),
        'irq': ('interrupts', 'rate'),
        'vmpage_action': ('actions', 'rate'),
        'vmpage_io': ('iops', 'rate'),
        'vmpage_number': ('pages', 'gauge'),
        'vmpage_faults': ('faults', 'rate'),
        'disk_ops': ('iops', 'rate'),
        'disk_octets': ('bytes', 'rate'),
        'disk_time': ('secs', 'gauge'),
        'disk_merged': ('iops', 'gauge'),
        'memory': ('bytes', 'gauge'),
        'swap': ('swap', 'gauge'),
        'swap_io': ('iops', 'gauge'),
        'df_complex': ('bytes', 'gauge'),
        'ps_state': ('processes', 'gauge'),
        'ps_count': ('processes', 'gauge'),
        'ps_disk_ops': ('iops', 'rate'),
        'ps_disk_octets': ('bytes', 'rate'),
        'ps_stacksize': ('bytes', 'gauge'),
        'ps_code': ('bytes', 'gauge'),
        'ps_rss': ('bytes', 'gauge'),
        'ps_pagefaults': ('faults', 'rate'),
        'fork_rate': ('forks', 'rate'),
        'time_dispersion': ('secs', 'gauge'),
        'frequency_offset': ('secs', 'gauge'),
        'delay': ('secs', 'gauge'),
        'time_offset': ('secs', 'gauge'),
        'users': ('users', 'gauge'),
        'contextswitch': ('switches', 'gauge'),
        'entropy': ('entropy', 'gauge'),
        'conntrack': ('conntrack', 'gauge'),
        'counter': ('1', 'rate')
    }
    targets = [{
        'match': '^collectd\.(?P<server>.+?)\.(?P<collectd_plugin>.+?)(?:-(?P<collectd_plugin_instance>.+?))?\.(?P<type>.+?)(?:-(?P<type_instance>.+?))?\.(?P<value>.+)$',
        'target_type': 'unknown',
        'configure': [
            lambda self, target: self.add_tag(target, 'source', 'collectd'),
            lambda self, target: self.add_tag(target, 'target_type', self.collectd_target_type(target)),
            lambda self, target: self.add_tag(target, 'what', self.collectd_what(target))
        ]
    }]

    @classmethod
    def collectd_desc(self, target):
        return self.collectd_types.get(target['tags']['type'], (target['tags']['type'], 'gauge'))

    @classmethod
    def collectd_target_type(self, target):
        return self.collectd_desc(target)[1]

    @classmethod
    def collectd_what(self, target):
        return self.collectd_desc(target)[0]

# vim: ts=4 et sw=4:
