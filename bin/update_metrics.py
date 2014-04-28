#!/usr/bin/env python2
import os
import sys
from argparse import ArgumentParser

from graph_explorer import config
from graph_explorer.backend import Backend
from graph_explorer import structured_metrics
from graph_explorer.log import make_logger


def main():
    parser = ArgumentParser(description="Update Graph Explorer metrics")
    parser.add_argument("configfile", metavar="CONFIG_FILENAME", type=str)
    args = parser.parse_args()

    config.init(args.configfile)

    logger = make_logger('update_metrics', config)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

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


if __name__ == "__main__":
    sys.exit(main())
