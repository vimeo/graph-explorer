#!/usr/bin/env python2
import os
import sys

import config
from backend import Backend, make_config
from log import make_logger
import structured_metrics

config = make_config(config)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

logger = make_logger('update_metrics', config)

try:
    backend = Backend(config, logger)
    s_metrics = structured_metrics.StructuredMetrics(config, logger)
    errors = s_metrics.load_plugins()
    if len(errors) > 0:
        logger.warn('errors encountered while loading plugins:')
        for e in errors:
            print '\t%s' % e
    logger.info("fetching/saving metrics from graphite...")
    backend.download_metrics_json()
    logger.info("generating structured metrics data...")
    backend.update_data(s_metrics)
    logger.info("success!")
except Exception, e:  # pylint: disable=W0703
    logger.error("sorry, something went wrong: %s", e)
    from traceback import print_exc
    print_exc()
    sys.exit(2)
