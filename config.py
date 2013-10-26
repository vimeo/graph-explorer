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
anthracite_url = None

## graph explorer daemon needs to connect to elasticsearch,
# you typically run an ES on the same host as GE.
es_host = "localhost"
es_port = 9200
# irrespective of 'limit', never get more metrics than this from ES:
limit_es_metrics = 10000
