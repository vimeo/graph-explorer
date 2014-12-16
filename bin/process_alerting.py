#!/usr/bin/python2
from graph_explorer.alerting import msg_codes, Db, Result
from graph_explorer.alerting.emailoutput import EmailOutput
from graph_explorer import structured_metrics
from graph_explorer import config, preferences
import os
from argparse import ArgumentParser
import time

app_dir = os.path.dirname(__file__)
if app_dir:
    os.chdir(app_dir)

parser = ArgumentParser(description="Process alerting rules")
parser.add_argument("configfile", metavar="CONFIG_FILENAME", type=str)
args = parser.parse_args()

config.init(args.configfile)
config.valid_or_die()


if not config.alerting:
    print "alerting disabled in config"
    os.exit(0)

start_timestamp = int(time.time())
success = True

s_metrics = structured_metrics.StructuredMetrics(config)
db = Db(config.alerting_db)
rules = db.get_rules()

output = EmailOutput(config)


def submit_maybe(result):
    if result.to_report():
        output.submit(result)
        db.save_notification(result)
        print "sent notification!"
    else:
        print "no notification"

for rule in rules:
    print " >>> rule ", rule.name()
    if not rule.active:
        print "inactive. skipping..."
        continue
    try:
        results, worst = rule.check_values(config, s_metrics, preferences)
    except Exception, e:
        result = Result(db, config, "Could not process your rule", 3, rule)
        result.body = ["Could not process your rule", str(e)]
        print result.log()
        submit_maybe(result)
        success = False
        continue
    result = Result(db, config, "%s is %s" % (rule.name(), msg_codes[worst]), worst, rule)
    for (target, value, status) in results:
        line = " * %s value %s --> status %s" % (target, value, msg_codes[status])
        result.body.append(line)
    print result.log()
    submit_maybe(result)

if not rules:
    print "no rules defined!"

if success:
    print "run %d OK" % start_timestamp
else:
    print "run %d FAIL" % start_timestamp
