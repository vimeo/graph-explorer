import sys
from ConfigParser import SafeConfigParser


class DummyConfigParser(object):
    def __getattr__(self, name):
        raise Exception("Configuration not initialised")


parser = DummyConfigParser()


def init(filename):
    global parser, config
    parser = SafeConfigParser()
    parser.read([filename])

    # This is for backward-compatability. Code should probably be changed to get values
    # from the ConfigParser object directly.
    config = sys.modules[__name__]
    config.listen_host = parser.get("graph_explorer", "listen_host")
    config.listen_port = parser.getint("graph_explorer", "listen_port")
    config.filename_metrics = parser.get("graph_explorer", "filename_metrics")
    config.log_file = parser.get("graph_explorer", "log_file")
    
    config.graphite_url_server = parser.get("graphite", "url_server")
    config.graphite_url_client = parser.get("graphite", "url_client")
    config.graphite_username = parser.get("graphite", "username") or None
    config.graphite_password = parser.get("graphite", "password") or None

    config.anthracite_url = parser.get("anthracite", "url") or None
    config.anthracite_add_url = parser.get("anthracite", "add_url") or None

    config.metric_plugin_dirs = parser.get("plugins", "metric_plugin_dirs").splitlines()

    config.es_host = parser.get("elasticsearch", "host")
    config.es_port = parser.getint("elasticsearch", "port")
    config.es_index = parser.get("elasticsearch", "index")
    config.limit_es_metrics = parser.getint("elasticsearch", "limit_es_metrics")
    config.process_native_proto2 = parser.getboolean("elasticsearch", "process_native_proto2")

    config.alerting = parser.getboolean("alerting", "alerting")
    config.alerting_db = parser.get("alerting", "db")
    config.alerting_from = parser.get("alerting", "from")
    config.alert_backoff = parser.getint("alerting", "backoff")
    config.alerting_base_uri = parser.get("alerting", "base_uri")

    config.collectd_StoreRates = parser.getboolean("collectd", "StoreRates")
    config.collectd_prefix = parser.get("collectd", "prefix")
