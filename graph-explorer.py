#!/usr/bin/env python2

import os
from bottle import run, debug, PasteServer
import config

os.chdir(os.path.dirname(__file__))

debug(True)
run('app', reloader=True, host=config.listen_host, port=config.listen_port, server=PasteServer)
