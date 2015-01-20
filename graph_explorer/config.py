import sys
from ConfigParser import SafeConfigParser, NoOptionError, NoSectionError
from graph_explorer.validation import ConfigValidator


class DummyConfigParser(object):
    def __getattr__(self, name):
        raise Exception("Configuration not initialised")


parser = DummyConfigParser()
file_name = ""


def init(filename):
    global parser, config, file_name
    file_name = filename
    parser = SafeConfigParser()
    parser.readfp(open(filename))

    # This is for backward-compatability. Code should probably be changed to get values
    # from the ConfigParser object directly.
    # no this is because we want to be able to validate the whole thing
    config = sys.modules[__name__]

    # no config parser allows for a value not to exist, will always raise exception
    # but we want to be able to validate later and show all bad and missing values.
    def get(section, option):
        try:
            return parser.get(section, option)
        except (NoOptionError, NoSectionError):
            pass
        return None

    def getlist(section, option):
        try:
            list_str = parser.get(section, option)
            return list_str.splitlines()
        except (NoOptionError, NoSectionError):
            pass
        return None

    def getint(section, option):
        try:
            return parser.getint(section, option)
        except (NoOptionError, NoSectionError):
            pass
        return None

    def getboolean(section, option):
        try:
            return parser.getboolean(section, option)
        except (NoOptionError, NoSectionError):
            pass
        return None

    config.listen_host = get("graph_explorer", "listen_host")
    config.listen_port = getint("graph_explorer", "listen_port")
    config.filename_metrics = get("graph_explorer", "filename_metrics")
    config.log_file = get("graph_explorer", "log_file")

    config.graphite_url_server = get("graphite", "url_server")
    config.graphite_url_client = get("graphite", "url_client")
    config.graphite_username = get("graphite", "username") or None
    config.graphite_password = get("graphite", "password") or None

    config.anthracite_host = get("anthracite", "host") or None
    config.anthracite_port = getint("anthracite", "port") or 9200
    config.anthracite_index = get("anthracite", "index") or None
    config.anthracite_add_url = get("anthracite", "add_url") or None

    config.locations_plugins_structured_metrics = getlist("locations", "plugins_structured_metrics")
    config.locations_dashboards = getlist("locations", "dashboards")

    config.es_host = get("elasticsearch", "host")
    config.es_port = getint("elasticsearch", "port")
    config.es_index = get("elasticsearch", "index")
    config.limit_es_metrics = getint("elasticsearch", "limit_es_metrics")
    config.process_native_proto2 = getboolean("elasticsearch", "process_native_proto2")

    config.alerting = getboolean("alerting", "alerting")
    config.alerting_db = get("alerting", "db")
    config.alerting_smtp = get("alerting", "smtp")
    config.alerting_from = get("alerting", "from")
    config.alert_backoff = getint("alerting", "backoff")
    config.alerting_base_uri = get("alerting", "base_uri")

    config.collectd_StoreRates = getboolean("collectd", "StoreRates")
    config.collectd_prefix = get("collectd", "prefix")


def valid_or_die():
    global config, file_name
    config = sys.modules[__name__]
    c = ConfigValidator(obj=config)
    if c.validate():
        return
    print "Configuration errors (%s):" % file_name
    for (key, err) in c.errors.items():
        print key,
        for e in err:
            print "\n    %s" % e
    sys.exit(1)
