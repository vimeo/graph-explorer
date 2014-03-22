# Note:
# * these demonstrate some id matching, tag matching, etc. there's usually
#    multiple ways to achieve the same result.
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
        'query': 'diskspace unit=B used _var',
        'desc': '/var usage'
    },
    {
        'query': 'diskspace unit=B used _var avg by server',
        'desc': '/var usage, average of all servers'
    },
    {
        'query': 'diskspace unit=B/s used _var',
        'desc': 'change in /var usage'
    },
    {
        'query': 'iostat rate (read|write) byte',
        'desc': 'read/write B/s'  # TODO: a better way to paraphrase these. some kind of aggregation?
    },
    {
        'query': 'stack plugin=load group by type !05 !15 avg over 30M',
        'desc': 'compare load across machines'  # no 5,15 minutely avg, we already have 1 minutely
    },
    {
        'query': 'device=eth0 (rx|tx) bit avg by type sum by server avg over 1h',
        'desc': 'network traffic'
    }
]
suggested_queries = {
    'notes': 'these will only work if you have the corresponding metrics',
    'queries': queries
}
