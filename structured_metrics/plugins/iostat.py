from . import Plugin


class IostatPlugin(Plugin):
    '''
    corresponds to diamond diskusage plugin
    '''
    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.iostat\.(?P<device>[^\.]+)\.(?P<wt>.*_per_second)$',
            'target_type': 'rate',
        },
        {
            'match': '^servers\.(?P<server>[^\.]+)\.iostat\.(?P<device>[^\.]+)\.(?P<wt>.*)$',
            'target_type': 'gauge',
        }
    ]

    def sanitize(self, target):
        # NOTE: a bunch of these are probably not accurate. TODO: someone has
        # to go over these, preferrably someone familiar with the diamond
        # plugin or /proc/diskstats.
        sanitizer = {
            'average_queue_length': ('iops', 'in queue'),
            'average_request_size_byte': ('B', 'iop avg size'),
            'await': ('ms', 'iop service time'),
            'concurrent_io': ('iops', 'concurrent'),
            'io': ('io', None),
            'io_in_progress': ('iops', 'in_progress'),
            'io_milliseconds': ('ms', 'io'),
            'io_milliseconds_weighted': ('ms_weighted', 'io'),
            'iops': ('iops', None),
            'read_await': ('ms', 'read service time'),
            'read_byte': ('B', 'read'),
            'read_byte_per_second': ('B', 'read'),
            'read_requests_merged': ('read_requests', 'merged'),
            'read_requests_merged_per_second': ('read_requests', 'merged'),
            'reads': ('reads', None),
            'reads_byte': ('B', 'read'),
            'reads_merged': ('reads', 'merged'),
            'reads_milliseconds': ('ms', 'spent reading'),
            'reads_per_second': ('reads', None),
            'service_time': ('ms', 'service time'),
            'util_percentage': ('utilisation', None, 'pct'),
            'write_await': ('ms', 'write service time'),
            'write_byte': ('B', 'written'),
            'write_byte_per_second': ('B', 'written'),
            'write_requests_merged': ('write_requests', 'merged'),
            'write_requests_merged_per_second': ('write_requests', 'merged'),
            'writes': ('writes', None),
            'writes_byte': ('B', 'written'),
            'writes_merged': ('writes', 'merged'),
            'writes_milliseconds': ('ms', 'spent writing'),
            'writes_per_second': ('writes', None)
        }
        wt = target['tags']['wt']
        target['tags']['unit'] = sanitizer[wt][0]
        if sanitizer[wt][1] is not None:
            target['tags']['type'] = sanitizer[wt][1]
        if len(sanitizer[wt]) > 2:
            target['tags']['target_type'] = target['tags']['target_type'] + '_' + sanitizer[wt][2]
        del target['tags']['wt']
        return None
# vim: ts=4 et sw=4:
