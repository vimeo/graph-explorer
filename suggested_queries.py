# Note:
# * example queries will only work if you have corresponding metrics, of course
# * these demonstrate some id matching, tag matching, etc. there's usually
#    multiple ways to achieve the same result.
# * these examples are a bit specific to vimeo things (e.g. dfvimeo* hostnames)
# * tags here do not necessarily correspond to tags in targets. they are for
#   informative purposes only.  although we could (automatically) display the
#   tags from the query (and make keys implicit in the color of the label or
#   something, to save space), I don't do that because:
#   * id matching allows shorter, easier hackable queries.  this hides
#   information which would otherwise be available as tags.
#   * some tags don't need to be mentioned explicitly (i.e. type=byte_used can
#   be assumed for disk usage)
#   * some tags can be paraphrased per env-specific rules (usually the case for
#   hostnames)
queries = [
    {
        'query': 'swift_object_server rate',
        'desc': 'events rates',
        'tags': ['swift', 'dfs']
    },
    {
        'query': 'diskspace count type=byte_used mountpoint:_srv server:dfvimeodfs',
        'desc': '/srv/* usage',
        'tags': ['disk', 'dfs']
    },
    {
        'query': 'diskspace count type=byte_used _var dfvimeodfs',
        'desc': '/var usage',
        'tags': ['disk', 'dfs']
    },
    {
        'query': 'diskspace rate !giga byte_used _var dfvimeodfs',
        'desc': 'change in /var usage',
        'tags': ['disk', 'dfs']
    },
    {
        'query': 'proxy_server timer (lower|upper_90)',
        'desc': 'http request timings',
        'tags': ['swift', 'dfsproxy']
    },
    {
        'query': 'object_server timer (lower|upper_90)',
        'desc': 'http request timings',
        'tags': ['swift', 'dfs']
    },
    {
        'query': 'container_metrics',
        'desc': 'container metrics',
        'tags': ['swift']
    },
    {
        'query': 'target_type:dispersion group by type !copies_(found|expected)',
        'desc': 'dispersion (highlevel health)',  # copies_(found|expected) filtered out because that info is included in the percentage
        'tags': ['swift']
    },
    {
        'query': 'iostat rate (read|write)_byte dfvimeodfs',
        'desc': 'read/write B/s',  # TODO: a better way to paraphrase these. some kind of aggregation?
        'tags': ['disk', 'dfs', 'dfsproxy']
    },
    {
        'query': 'load count group by type !05 !15',
        'desc': 'compare load across machines',  # no 5,15 minutely avg, we already have 1 minutely
        'tags': ['load', '*']
    },
    {
        'query': 'bond1 (rx|tx)_bit group by type server:dfs',
        'desc': 'storage network traffic',
        'tags': ['swift', 'dfs', 'dfsproxy']
    },
    {
        'query': 'network _bit',
        'desc': 'traffic in bit on all interfaces',
        'tags': ['network', '*']
    },
    {
        'query': 'plugin=statsd',
        'desc': 'statsd health part 1: statsd.js',
        'tags': ['statsd']
    },
    {
        'query': 'plugin=udp server:statsd group by type',
        'desc': 'statsd health part 2: udp',
        'tags': ['statsd', 'udp']
    }

]
suggested_queries = {
    'notes': 'swift means the app.<br/>dfs means the object servers, dfsproxy the proxy servers',
    'queries': queries
}
