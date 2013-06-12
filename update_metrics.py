#!/usr/bin/env python2
import os
import sys
import urllib2
import logging

import config
from backend import Backend, MetricsError
import structured_metrics

os.chdir(os.path.dirname(__file__))

logger = logging.getLogger('update_metrics')
logger.setLevel(logging.DEBUG)
chandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
chandler.setFormatter(formatter)
logger.addHandler(chandler)
if config.log_file:
    fhandler = logging.FileHandler(config.log_file)
    fhandler.setFormatter(formatter)
    logger.addHandler(fhandler)

try:
    backend = Backend(config, logger)
    s_metrics = structured_metrics.StructuredMetrics()
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
except Exception, e:
    logger.error("sorry, something went wrong: %s", e)
    sys.exit(2)
