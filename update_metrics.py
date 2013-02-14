#!/usr/bin/env python2
import os
import sys
import urllib2


import config
from backend import Backend, MetricsError
try:
    backend = Backend(config)
    print "fetching/saving metrics from graphite..."
    backend.download_metrics_json()
    print "success!"
    print "if the server is running, I'll hit the refresh endpoint.."
    response = urllib2.urlopen("http://localhost:%i/refresh_data" % config.listen_port)
    if response.getcode() != 200:
        print "failed"
    print response.read()

except urllib2.URLError, e:
    sys.stderr.write("something went wrong (maybe/sortof)..: %s" % e)
    sys.exit(1)
except Exception, e:
    sys.stderr.write("sorry, something went wrong: %s" % e)
    sys.exit(2)
