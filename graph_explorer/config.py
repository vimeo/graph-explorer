listen_host = '0.0.0.0'  # defaults to "all interfaces"
listen_port = 8080
filename_metrics = 'metrics.json'
log_file = 'graph-explorer.log'

## need to connect to graphite
# the url that the graph-explorer daemon will use to connect to graphite
graphite_url_server = 'http://localhost'
# the url that the graph renderer in browser will use to connect to graphite
graphite_url_client = 'http://graphite.machine.dns'
graphite_username = None
graphite_password = None

## optional, to get annotated events on your graphs
# (the clientside graph renderer talks directly to it)
# this will point to your anthracite index in elastic search
# anthracite_host = "localhost"
# anthracite_port = 9200
# anthracite_index = "anthracite"
anthracite_host = None
anthracite_port = None
anthracite_index = None

# url to add events by clicking on graphs. usually this is just an extra /events/add
# but if you use plugins the path can be different.  None to disable
# anthracite_add_url = "http://anthracite-machine/events/add"
anthracite_add_url = None

# load structured_metrics plugins from all of these directories, in order;
# the magic string "**builtins**" refers to the graph-explorer builtin
# plugins. if you don't want them loaded, take out "**builtins**".
metric_plugin_dirs = ('**builtins**',)

## graph explorer daemon needs to connect to elasticsearch,
# you typically run an ES on the same host as GE.
es_host = "localhost"
es_port = 9200
es_index = 'graphite_metrics2'
# irrespective of 'limit', never get more metrics than this from ES:
limit_es_metrics = 10000

# if metrics stored in graphite already look like proto2 (they contain a '='),
# should we still actively update them in ES?
# change to False if you already have them up to date in ES,
# for example when you use something like carbon-tagger.
process_native_proto2 = True


## for users of the alerting service
alerting = True
alerting_db = 'alerting.db'
alerting_from = 'Graph Explorer <graph-explorer@yourcompany.com>'
# per rule, max 10 notifications per this many seconds.
alert_backoff = 30 * 60
# base location of graph-explorer, in emails we'll refer to this + '/rules/view/id'
alerting_base_uri = 'http://graph-explorer:8080'


## for users of collectd
# whether the StoreRates is set in your collectd write_graphite plugin config
collectd_StoreRates = True
collectd_prefix = '^collectd\.'
