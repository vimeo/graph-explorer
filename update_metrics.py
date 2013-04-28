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
    backend = Backend(config)
    s_metrics = structured_metrics.StructuredMetrics()
    s_metrics.load_plugins()
    logger.info("fetching/saving metrics from graphite...")
    backend.download_metrics_json()
    backend.update_data(s_metrics) # cache these configs to disk file
    logger.info("success!")
except Exception, e:
    logger.error("sorry, something went wrong: %s", e)
    sys.exit(2)
