#!/usr/bin/env python2

from bottle import run, debug
from config import *

debug(True)
run('app', reloader=True, host=listen_host, port=listen_port)

