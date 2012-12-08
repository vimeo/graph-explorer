#!/usr/bin/env python2

from bottle import run, debug
import config

debug(True)
run('app', reloader=True, host=config.listen_host, port=config.listen_port)
