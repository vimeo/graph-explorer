#!/usr/bin/python2
import alerting
import config
from backend import make_config

config = make_config(config)

db = alerting.Db(config.alerting_db)
rules = db.get_rules()
for rule in rules:
    print "rule", rule
    try:
        value = rule.get_value(config)
    except Exception, e:
        print "could not process:", e
        continue
    print "value:", value
    status = rule.check(value)
    print "check:", status
    msg_codes = ['OK', 'WARN', 'CRITICAL']
    msg = "GE %s %s is %f" % (msg_codes[status], rule.expr, value)
    rule.notify_maybe(db, status, msg, config)
