#!/usr/bin/python2
import alerting
from backend import make_config
import os
import structured_metrics

app_dir = os.path.dirname(__file__)
if app_dir:
    os.chdir(app_dir)

import config
config = make_config(config)
import preferences

s_metrics = structured_metrics.StructuredMetrics(config)

db = alerting.Db(config.alerting_db)
rules = db.get_rules()

msg_codes = ['OK', 'WARN', 'CRITICAL', 'UNKNOWN']

for rule in rules:
    content = [
        "==== %s ====" % rule.expr,
        " val_warn: %f" % rule.val_warn,
        " val_crit: %f" % rule.val_crit,
        " dest    : %s" % rule.dest
    ]
    print "\n".join(content)

    try:
        results, worst = rule.check_values(config, s_metrics, preferences)
    except Exception, e:
        print "could not process:", e
        rule.notify_maybe(db, 3, "Could not process your rule", e, config)
        continue
    for (target, value, code) in results:
        line = " * %s %f %s" % (target, value, msg_codes[code])
        print line
        content.append(line)

    subject = "%s is %s" % (rule.expr, msg_codes[worst])
    rule.notify_maybe(db, worst, subject, "\n".join(content), config)
