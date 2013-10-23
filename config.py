listen_host = '0.0.0.0'  # defaults to "all interfaces"
listen_port = 8080
filename_metrics = 'metrics.json'
log_file = 'graph-explorer.log'

## need to connect to graphite
# (url must work from both GE server and clientside browser!)
graphite_url = 'http://graphitemachine'
graphite_username = None
graphite_password = None

## optional, to get annotated events on your graphs
anthracite_url = None

## elasticsearch
es_host = "elasticsearch_host"
es_port = 9200
# irrespective of 'limit', never get more metrics than this from ES:
limit_es_metrics = 10000
