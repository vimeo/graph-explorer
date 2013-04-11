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
        'query': 'diskspace gauge what=bytes used mountpoint:_srv server:dfvimeodfs',
        'desc': '/srv/* usage',
        'tags': ['disk', 'dfs']
    },
    {
        'query': 'diskspace gauge what=bytes used _var dfvimeodfs',
        'desc': '/var usage',
        'tags': ['disk', 'dfs']
    },
    {
        'query': 'diskspace rate !giga bytes used _var dfvimeodfs',
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
        'query': 'container_metrics group by what',
        'desc': 'container metrics',
        'tags': ['swift']
    },
    {
        'query': 'category:dispersion group by type',  # this means errors aren't shown, cause they won't have a type.
        'desc': 'dispersion (highlevel health)',
        'tags': ['swift']
    },
    {
        'query': 'iostat rate (read|write) byte dfvimeodfs',
        'desc': 'read/write B/s',  # TODO: a better way to paraphrase these. some kind of aggregation?
        'tags': ['disk', 'dfs', 'dfsproxy']
    },
    {
        'query': 'plugin=load group by type !05 !15',
        'desc': 'compare load across machines',  # no 5,15 minutely avg, we already have 1 minutely
        'tags': ['load', '*']
    },
    {
        'query': 'bond. (rx|tx) bit group by type server:dfs',
        'desc': 'storage network traffic',
        'tags': ['swift', 'dfs', 'dfsproxy']
    },
    {
        'query': 'network bits',
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
