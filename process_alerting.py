#!/usr/bin/python2
import alerting
from backend import make_config
import os

app_dir = os.path.dirname(__file__)
if app_dir:
    os.chdir(app_dir)

import config
config = make_config(config)

db = alerting.Db(config.alerting_db)
rules = db.get_rules()
for rule in rules:
    print("%80s" % rule),
    try:
        value = rule.get_value(config)
    except Exception, e:
        print "could not process:", e
        continue
    print("%15s" % value),
    status = rule.check(value)
    msg_codes = ['OK', 'WARN', 'CRITICAL']
    print("%10s" % msg_codes[status]),
    msg = "GE %s %s is %f" % (msg_codes[status], rule.expr, value)
    rule.notify_maybe(db, status, msg, config)
