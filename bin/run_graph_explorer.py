#!/usr/bin/env python2

import os
import sys
from argparse import ArgumentParser
from bottle import run, debug, PasteServer
from graph_explorer import config


def main():
    parser = ArgumentParser(description="Run Graph Explorer")
    parser.add_argument("configfile", metavar="CONFIG_FILENAME", type=str)
    parser.add_argument("--debug", type=bool)
    args = parser.parse_args()

    config.init(args.configfile)
    config.valid_or_die()

    # tmp disabled. breaks config loading
    #app_dir = os.path.dirname(__file__)
    #if app_dir:
    #    os.chdir(app_dir)

    debug(args.debug)
    run('graph_explorer.app',
        reloader=True,
        host=config.listen_host,
        port=config.listen_port,
        server=PasteServer)


if __name__ == "__main__":
    sys.exit(main())
