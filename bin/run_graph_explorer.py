#!/usr/bin/env python2

import os
from bottle import run, debug, PasteServer
from graph_explorer import config

debug(True)
run('graph_explorer.app',
    reloader=True,
    host=config.listen_host,
    port=config.listen_port,
    server=PasteServer)
