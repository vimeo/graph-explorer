#!/usr/bin/env python2
"""
this program shows how the proto1 -> proto2 upgrade looks like for
all metrics given as cmdline arguments.
very convenient to verify the working of plugins etc.
"""

import sys
from pprint import pprint
import logging

from graph_explorer import structured_metrics
from graph_explorer import config
from graph_explorer.log import make_logger

if len(sys.argv) < 3:
    print "check_update_metric.py <config file> <metric1> [<metric2> [<metric3...]]"
    sys.exit(1)

config.init(sys.argv[1])
config.valid_or_die()


logger = make_logger('check_update_metric', config)
logger.setLevel(logging.WARN)

s_metrics = structured_metrics.StructuredMetrics(config, logger)
errors = s_metrics.load_plugins()
if len(errors) > 0:
    print 'errors encountered while loading plugins:'
    for e in errors:
        print '\t%s' % e
for v in s_metrics.list_metrics(sys.argv[2:]).values():
    pprint(v)
