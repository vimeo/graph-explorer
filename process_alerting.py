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
        "==== %s ====" % rule.name(),
        " val_warn: %f" % rule.val_warn,
        " val_crit: %f" % rule.val_crit,
        "\nCurrent value(s):\n"
    ]
    print "\n".join(content)

    try:
        results, worst = rule.check_values(config, s_metrics, preferences)
    except Exception, e:
        print "could not process:", e
        content = "\n".join(["Could not process your rule", str(rule), str(e)])
        rule.notify_maybe(db, 3, "Could not process your rule", content, config)
        continue
    for (target, value, code) in results:
        line = " * %s value %s --> status %s" % (target, value, msg_codes[code])
        print line
        content.append(line)

    content.append("\n\nThis email is sent to %s" % rule.dest)

    subject = "%s is %s" % (rule.name(), msg_codes[worst])
    sent = rule.notify_maybe(db, worst, subject, "\n".join(content), config)
    if sent:
        print "sent notification!"
    else:
        print "no notification"
