#!/usr/bin/env python2
import os
import sys
import urllib2
import logging

import config
from backend import Backend, MetricsError

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
    logger.info("fetching/saving metrics from graphite...")
    backend.download_metrics_json()
    logger.info("success!")
    logger.info("if the server is running, I'll hit the refresh endpoint..")
    response = urllib2.urlopen("http://localhost:%i/refresh_data" % config.listen_port)
    if response.getcode() != 200:
        logger.warning("failed")
    logger.debug(response.read())

except urllib2.URLError, e:
    logger.error("something went wrong (maybe/sortof)..: %s", e)
    sys.exit(1)
except Exception, e:
    logger.error("sorry, something went wrong: %s", e)
    sys.exit(2)
