#!/usr/bin/env python2

import os
import sys
from bottle import run, debug, PasteServer
import config
from validation import ConfigValidator

c = ConfigValidator(obj=config)
if not c.validate():
    print "there's a problem with your configuration:"
    for (key, err) in c.errors.items():
        print key,
        for e in err:
            print "\n    ", e
    sys.exit(1)


app_dir = os.path.dirname(__file__)
if app_dir:
    os.chdir(app_dir)

debug(True)
run('app', reloader=True, debug=True, host=config.listen_host, port=config.listen_port, server=PasteServer)
