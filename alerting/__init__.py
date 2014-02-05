from types import IntType
import urllib
import urllib2
from urlparse import urljoin
import json
import time
import sqlite3
from query import Query
import graphs as g


msg_codes = ['OK', 'WARN', 'CRITICAL', 'UNKNOWN']


class Rule():
    def __init__(self, Id, alias, expr, val_warn, val_crit, dest, active):
        self.Id = Id
        self.alias = alias
        self.expr = expr
        self.val_warn = val_warn
        self.val_crit = val_crit
        self.dest = dest
        self.active = active
        self.results = None

    def __str__(self):
        return "Rule %s (id %d)" % (self.name(), self.Id)

    def name(self):
        return self.alias if self.alias else self.expr

    def is_geql(self):
        return " " in self.expr

    def clean_form(self):
        self.Id = int(self.Id)
        self.val_warn = float(self.val_warn)
        self.val_crit = float(self.val_crit)

    def check_values(self, config, s_metrics, preferences):
        worst = 0
        results = []
        if " " in self.expr:  # looks like a GEQL query
            query = Query(self.expr)
            (query, targets_matching) = s_metrics.matching(query)
            graphs_targets_matching = g.build_from_targets(targets_matching, query, preferences)[0]
            for graph_id, graph in graphs_targets_matching.items():
                for target in graph['targets']:
                    target = target['target']
                    value = check_graphite(target, config)
                    status = self.check(value)
                    results.append((target, value, status))
                    # if worst so far is ok and we have an unknown, that takes precedence
                    if status == 3 and worst == 0:
                        worst = 3
                    # if the current status is not unknown and it's worse than whatever we have, update worst
                    if status != 3 and status > worst:
                        worst = status

        else:
            target = self.expr
            value = check_graphite(target, config)
            status = self.check(value)
            results.append((target, value, status))
            if status > worst:
                worst = status
        self.results = results
        return results, worst

    def check(self, value):
        if value is None:
            return 3
        # uses nagios-style statuses: 0 ok, 1 warn, 2 crit, 3 unknown
        # the higher the value, the worse. except for unknown which is somewhere just below warn.
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


class Result():

    def __init__(self, db, config, title, status, rule):
        self.db = db
        self.config = config
        self.title = title
        self.status = status
        self.status_str = msg_codes[status]
        self.rule = rule
        self.body = []

    def to_report(self):
        last = self.db.get_last_notifications(self.rule.Id)
        if last:
            # don't report what we reported last
            if last[0]['status'] == self.status:
                return False
            # don't send any message if we've sent more than 10 in the backoff interval
            if len(last) == 10 and last[-1]['timestamp'] >= int(time.time()) - self.config.alert_backoff:
                return False
        return True

    def log(self):
        return "%s is %s: %s\n%s" % (self.rule.name(), self.status_str, self.title, "\n".join(self.body))


class Db():
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.cursor = self.conn.cursor()
        self.exists = False

    def assure_db(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS rules
                (id integer primary key autoincrement, expr text, val_warn float, val_crit float, dest text)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS notifications
                (id integer primary key autoincrement, rule_id integer, timestamp int, status int)""")
        self.exists = True

    def get_last_notifications(self, rule_id):
        self.assure_db()
        query = 'SELECT timestamp, status from notifications where rule_id == ? order by timestamp desc limit 10'
        self.cursor.execute(query, (rule_id,))
        rows = self.cursor.fetchall()
        notifications = []
        for row in rows:
            notifications.append({
                'timestamp': row[0],
                'status': row[1]
            })
        return notifications

    def save_notification(self, result):
        self.assure_db()
        self.cursor.execute(
            "INSERT INTO notifications (rule_id, timestamp, status) VALUES (?,?,?)",
            (result.rule.Id, int(time.time()), result.status)
        )
        self.conn.commit()

    def add_rule(self, rule):
        self.assure_db()
        self.cursor.execute(
            "INSERT INTO rules (alias, expr, val_warn, val_crit, active, dest) VALUES (?,?,?,?,?,?)",
            (rule.alias, rule.expr, rule.val_warn, rule.val_crit, rule.active, rule.dest)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def delete_rule(self, Id):
        # note, this doesn't check if the rule existed in the first place..
        assert type(Id) is IntType or Id.isdigit(), "Id must be an integer: %r" % Id
        self.assure_db()
        self.cursor.execute("DELETE FROM rules WHERE ROWID == " + str(Id))
        self.conn.commit()

    def edit_rule(self, rule):
        self.assure_db()
        rule.clean_form()
        self.cursor.execute(
            "UPDATE rules SET alias = ?, expr = ?, val_warn = ?, val_crit = ?, active = ?, dest = ? WHERE id = ?",
            (rule.alias, rule.expr, rule.val_warn, rule.val_crit, rule.active, rule.dest, rule.Id)
        )
        self.conn.commit()

    def get_rules(self, metric_id=None):
        self.assure_db()
        query = 'SELECT id, alias, expr, val_warn, val_crit, dest, active FROM rules'
        if metric_id is not None:
            query += " where expr like '%%%s%%'"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        rules = list()
        for row in rows:
            rules.append(Rule(*row))
        return rules

    def get_rule(self, Id):
        self.assure_db()
        query = 'SELECT id, alias, expr, val_warn, val_crit, dest, active FROM rules where id = ?'
        self.cursor.execute(query, (Id,))
        row = self.cursor.fetchone()
        rule = Rule(*row)
        return rule


def rule_from_form(form):
    alias = form.alias.data
    expr = form.expr.data
    val_warn = float(form.val_warn.data)
    val_crit = float(form.val_crit.data)
    active = form.active.data
    dest = form.dest.data
    rule = Rule(None, alias, expr, val_warn, val_crit, dest, active)
    return rule


def check_graphite(target, config):
    url = urljoin(config.graphite_url_server, "/render/?from=-3minutes&format=json")
    values = {'target': target}
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    json_data = json.load(response)
    if not len(json_data):
        raise Exception("graphite did not return data for %s" % target)
    # get the last non-null value
    last_dp = None
    for dp in json_data[0]['datapoints']:
        if dp[0] is not None:
            last_dp = dp
    if last_dp is None:
        return None
    return last_dp[0]


def get_png(targets, config, width=800):
    url = urljoin(config.graphite_url_server, "/render/?from=-8hours&width=%d" % width)
    # TODO: for some reason sending as POST somehow gets the same graph in multiple
    # subsequent alerts. yeah wtf.
    #data = urllib.urlencode([('target', target) for target in targets])
    data = None
    # so for now use GET and hope/assume the url won't get too long (it could)
    for target in targets:
        url += "&target=" + target
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    return response.read()


class Output():
    pass
