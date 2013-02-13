#!/usr/bin/env python2
import os
import sys
import urllib2


import config
try:
    print "fetching/saving metrics from graphite..."
    response = urllib2.urlopen("%s/metrics/index.json" % config.graphite_url)
    m = open('%s.tmp' % config.filename_metrics, 'w')
    m.write(response.read())
    m.close()
    os.rename('%s.tmp' % config.filename_metrics, config.filename_metrics)
    print "done!"

except Exception, e:
    sys.stderr.write("sorry, something went wrong: %s" % e)
    sys.exit(1)
