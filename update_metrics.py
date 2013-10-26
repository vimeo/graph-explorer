#!/usr/bin/env python2
import os
import sys
import logging

import config
from backend import Backend, make_config
import structured_metrics

config = make_config(config)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

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
except Exception, e:
    logger.error("sorry, something went wrong: %s", e)
    from traceback import print_exc
    print_exc()
    sys.exit(2)
