queries = [
    'plugin=statsd',
    'plugin=carbon',
    {
        'query': 'plugin=udp server:statsd group by type',
        'desc': 'udp stats on statsd servers'
    }
]
