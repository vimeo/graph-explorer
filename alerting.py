from types import IntType
import urllib2
from urlparse import urljoin
import json
import time
import subprocess
import sqlite3


class Rule():
    def __init__(self, rowid, metric_id, expr, val_warn, val_crit):
        self.row_id = rowid
        self.metric_id = metric_id
        self.expr = expr
        self.val_warn = val_warn
        self.val_crit = val_crit
        self.validate()

    def __str__(self):
        return "Rule id=%d metric_id=%s expr=%s val_warn=%f, val_crit=%f" % (self.row_id, self.metric_id, self.expr, self.val_warn, self.val_crit)

    def validate(self):
        assert self.val_warn != self.val_crit

    def get_value(self, config):
        url = urljoin(config.graphite_url_server, "/render/?target=%s&from=-2minutes&format=json" % self.expr)
        response = urllib2.urlopen(url)
        json_data = json.load(response)
        assert len(json_data) < 2
        if not len(json_data):
            raise Exception("graphite did not return data for %s" % self.expr)
        # get the last non-null value
        last_dp = None
        for dp in json_data[0]['datapoints']:
            if dp[0] is not None:
                last_dp = dp
        assert last_dp is not None, "couldn't find any non-null datapoints"
        return last_dp[0]

    def check(self, value):
        # uses nagios-style codes: 0 ok, 1 warn, 2 crit
        # the lower the value, the worse
        if self.val_warn > self.val_crit:
            if value > self.val_warn:
                return 0
            if value > self.val_crit:
                return 1
            return 2
        # the higher the value, the worse
        else:
            if value < self.val_warn:
                return 0
            if value < self.val_crit:
                return 1
            return 2

    def notify_maybe(self, db, status, msg, config):
        if config.alert_cmd is None:
            return
        now = int(time.time())
        last = db.get_last_notification(self.row_id)
        if last and last['timestamp'] >= now - config.alert_backoff:
            return
        if last and last['status'] == status:
            return
        data = {
            'content': msg,
            'subject': msg
        }
        ret = subprocess.call(config.alert_cmd.format(**data), shell=True)
        if ret:
            raise Exception("alert_cmd failed")
        db.save_notification(self, now, status, msg)


class Db():
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.cursor = self.conn.cursor()
        self.exists = False

    def assure_db(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS rules
                (id integer primary key autoincrement, metric_id text, expr text, val_warn float, val_crit float)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS notifications
                (id integer primary key autoincrement, rule_id integer, timestamp int, status int)""")
        self.exists = True

    def get_last_notification(self, rule_id):
        self.assure_db()
        query = 'SELECT timestamp, status from notifications where rule_id == ? order by timestamp desc limit 1'
        self.cursor.execute(query, (rule_id,))
        row = self.cursor.fetchone()
        return {
            'timestamp': row[0],
            'status': row[1]
        }

    def save_notification(self, rule, timestamp, status, msg):
        self.assure_db()
        self.cursor.execute("INSERT INTO notifications (rule_id, timestamp, status) VALUES (?,?,?)", (rule.row_id, timestamp, status))
        self.conn.commit()

    def add_rule(self, rule):
        """
        can raise sqlite3 exceptions and any other exception means something's wrong with the data
        """
        self.assure_db()
        self.cursor.execute("INSERT INTO rules (metric_id, expr, val_warn, val_crit) VALUES (?,?,?,?)", (rule.metric_id, rule.expr, rule.val_warn, rule.val_crit))
        self.conn.commit()
        return self.cursor.lastrowid

    def delete_rule(self, rule_id):
        # note, this doesn't check if the rule existed in the first place..
        assert type(rule_id) is IntType or rule_id.isdigit(), "rule_id must be an integer: %r" % rule_id
        self.assure_db()
        self.cursor.execute("DELETE FROM rules WHERE ROWID == " + str(rule_id))
        self.conn.commit()

    def get_rules(self, metric_id=None):
        self.assure_db()
        query = 'SELECT id, metric_id, expr, val_warn, val_crit FROM rules'
        if metric_id is not None:
            query += " where metric_id =='%s'"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        rules = list()
        for row in rows:
            rules.append(Rule(*row))
        return rules
