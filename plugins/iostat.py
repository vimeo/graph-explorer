from . import Plugin


class IostatPlugin(Plugin):
    '''
    corresponds to diamond diskusage plugin
    '''
    targets = [
        {
            'match': '^servers\.(?P<server>[^\.]+)\.iostat\.(?P<device>[^\.]+)\.(?P<type>.*)$',
            'default_graph_options': {'state': 'stacked'},
            'target_type': 'gauge'
        },
        {
            'match': '^servers\.(?P<server>[^\.]+)\.iostat\.(?P<device>[^\.]+)\.(?P<type>.*)_per_second$',
            'default_graph_options': {'state': 'stacked', 'vtitle': 'events/s'},
            'target_type': 'rate'
        }
    ]

    def sanitize(self, target):
        # TODO: make sure there is a gauge and a rate of everything (!
        # _per_second), assign correct what, type tags
        '''
        'average_queue_length'
        'average_request_size_byte'
        'await'
        'concurrent_io'
        'io'
        'io_in_progress'
        'io_milliseconds'
        'io_milliseconds_weighted'
        'iops'
        'read_await'
        'read_byte'
        'read_byte_per_second'
        'read_requests_merged'
        'read_requests_merged_per_second'
        'reads'
        'reads_byte'
        'reads_merged'
        'reads_milliseconds'
        'reads_per_second'
        'service_time'
        'util_percentage'
        'write_await'
        'write_byte'
        'write_byte_per_second'
        'write_requests_merged'
        'write_requests_merged_per_second'
        'writes'
        'writes_byte'
        'writes_merged'
        'writes_milliseconds'
        'writes_per_second'
        '''
        return None
# vim: ts=4 et sw=4:
