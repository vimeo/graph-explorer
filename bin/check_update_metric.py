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
from graph_explorer.backend import make_config
from graph_explorer.log import make_logger

config = make_config(config)
logger = make_logger('check_update_metric', config)
logger.setLevel(logging.WARN)

s_metrics = structured_metrics.StructuredMetrics(config, logger)
errors = s_metrics.load_plugins()
if len(errors) > 0:
    print 'errors encountered while loading plugins:'
    for e in errors:
        print '\t%s' % e
for v in s_metrics.list_metrics(sys.argv[1:]).values():
    pprint(v)
