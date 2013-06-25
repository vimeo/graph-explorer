import os
import re
from inspect import isclass
import sre_constants
import MySQLdb


class PluginError(Exception):

    def __init__(self, plugin, msg, underlying_error):
        self.plugin = plugin
        self.msg = msg
        self.underlying_error = underlying_error

    def __str__(self):
        return "%s -> %s (%s)" % (self.plugin, self.msg, self.underlying_error)


class DB:
    def __init__(self, config):
        self.config = {
            'host': config.mysql_host,
            'user': config.mysql_user,
            'passwd': config.mysql_passwd,
            'db': config.mysql_db
        }
        self.connect()

    def connect(self):
        self.db = MySQLdb.connect(**self.config)
        self.cur = self.db.cursor()

    def execute(self, *args):
        try:
            self.cur.execute(*args)
        except MySQLdb.Error, e:
            if e.args[0] == 2013:  # Lost connection to MySQL server during query
                self.connect()
                self.cur.execute(*args)
            else:
                raise
        return self.cur

    def fetchone(self, *args):
        return self.cur.fetchone(*args)

    def fetchall(self, *args):
        return self.cur.fetchall(*args)

    def __getattr__(self, name):
        if name == 'lastrowid':
            return self.cur.lastrowid


class StructuredMetrics(object):

    def __init__(self, config):
        self.plugins = []
        self.db = DB(config)
        self.get_all_metrics()

    def load_plugins(self):
        '''
        loads all the plugins sub-modules
        returns encountered errors, doesn't raise them because
        whoever calls this function defines how any errors are
        handled. meanwhile, loading must continue
        '''
        from plugins import Plugin
        import plugins
        errors = []
        plugins_dir = os.path.dirname(plugins.__file__)
        wd = os.getcwd()
        os.chdir(plugins_dir)
        for f in os.listdir("."):
            if f == '__init__.py' or not f.endswith(".py"):
                continue
            module = f[:-3]
            try:
                imp = __import__('plugins.' + module, globals(), locals(), ['*'])
            except Exception, e:
                errors.append(PluginError(module, "Failed to add plugin '%s'" % module, e))
                continue

            for itemname in dir(imp):
                item = getattr(imp, itemname)
                if isclass(item) and item != Plugin and issubclass(item, Plugin):
                    try:
                        self.plugins.append((module, item()))
                    # regex error is too vague to stand on its own
                    except sre_constants.error, e:
                        e = "error problem parsing matching regex: %s" % e
                        errors.append(PluginError(module, "Failed to add plugin '%s'" % module, e))
                    except Exception, e:
                        errors.append(PluginError(module, "Failed to add plugin '%s'" % module, e))
        os.chdir(wd)
        # sort plugins by their matching priority
        self.plugins = sorted(self.plugins, key=lambda t: t[1].priority, reverse=True)
        return errors

    def list_targets(self, metrics):
        for plugin in self.plugins:
            (plugin_name, plugin_object) = plugin
            plugin_object.reset_target_yield_counters()
        targets = {}
        for metric in metrics:
            metric_matched = False
            for (i, plugin) in enumerate(self.plugins):
                (plugin_name, plugin_object) = plugin
                for (k, v) in plugin_object.find_targets(metric):
                    metric_matched = True
                    tags = v['tags']
                    if ('what' not in tags or 'target_type' not in tags) and 'unit' not in tags:
                        print "WARNING: metric", v, "doesn't have the mandatory tags. ignoring it..."
                    if v['graphite_metric'] != v['target']:
                        print "WARNING: deprecated: plugin %s yielded metric with different target then graphite metric for %s" % (plugin_name, v['graphite_metric'])
                        # TODO if we don't yield here, probably the catchall
                        # plugin will just yield it in an inferior way.
                    else:
                        # old style: what and target_type tags, new style: unit tag
                        # automatically add new style for all old style metrics
                        if 'unit' not in tags and 'what' in tags and 'target_type' in tags:
                            convert = {
                                'bytes': 'B',
                                'bits': 'b'
                            }
                            unit = convert.get(tags['what'], tags['what'])
                            if tags['target_type'] is 'rate':
                                v['tags']['unit'] = '%s/s' % unit
                            else:
                                v['tags']['unit'] = unit
                        targets[k] = v
                    if metric_matched:
                        break
        return targets

    def update_targets(self, metrics):
        targets = self.list_targets(metrics)
        for target in targets.values():
            tag_ids = []
            self.db.execute("DELETE FROM metrics_tags WHERE metric_id = %s", target['graphite_metric'])
            self.db.execute("DELETE from metrics WHERE metric_id = %s", target['graphite_metric'])
            self.db.execute("INSERT INTO metrics (metric_id) VALUES (%s)", target['graphite_metric'])
            for tag_key, tag_val in target['tags'].items():
                try:
                    self.db.execute("INSERT INTO tags (tag_key, tag_val) VALUES(%s, %s)",  (tag_key, tag_val))
                    tag_ids.append(self.db.lastrowid)
                except MySQLdb.Error, e:
                    if e.args[0] == 1062:
                        self.db.execute("SELECT tag_id FROM tags WHERE tag_key=%s AND tag_val=%s", (tag_key, tag_val))
                        row = self.db.fetchone()
                        tag_ids.append(row[0])
                    else:
                        raise
            for tag_id in tag_ids:
                self.db.execute("INSERT INTO metrics_tags (metric_id, tag_id) VALUES(%s, %s)", (target['graphite_metric'], tag_id))

    def load_metric(self, metric_id):
        self.db.execute("SELECT tags.tag_key, tags.tag_val FROM tags, metrics_tags WHERE metrics_tags.metric_id = %s AND metrics_tags.tag_id == tags.tag_id", metric_id)
        rows = self.db.fetchall()
        if rows:
            m = {'graphite_metric': metric_id, 'tags': {}}
            for row in rows:
                m['tags'][row[0]] = row[1]
            return m
        else:
            return None

    def get_all_metrics(self):
        # option 0: bypass querying mysql itself by gathering ALL metrics from
        # mysql, keeping them in memory, and querying in python
        print "GETTING ALL METRICS"
        self.db.execute("SELECT metrics_tags.metric_id, tags.tag_key, tags.tag_val FROM metrics_tags, tags WHERE metrics_tags.tag_id = tags.tag_id")
        print "BUILDING METRICS"
        m = self.build_metrics(self.db.fetchall())
        print "DONE"
        return m

    def count_metrics(self):
        self.db.execute("SELECT count(metric_id) from metrics")
        row = self.db.fetchone()
        return row[0]

    def regex_to_like(self, pattern):
        # if the pattern matches only safe characters, we don't need
        # to do an expensive regexp clause, we can use a like instead
        return re.match('[a-zA-Z_]*$', pattern) is not None

    def build_sql_query1(self, query):
        # option 1: just leverage the fact that all tag key/val info is in the key anyway
        # don't use the other tables.
        # this only works for native proto-2 metrics obviously
        conditions = []
        params = []
        for (k, data) in query.items():
            if 'match_tag_equality' in data:
                if data['match_tag_equality'][1]:
                    if data['negate']:
                        conditions.append("metric_id NOT REGEXP %s")
                    else:
                        conditions.append("metric_id REGEXP %s")
                    params.append("[^\.]%s=%s[\.$]" % data['match_tag_equality'])
                else:
                    if data['negate']:
                        conditions.append("metric_id NOT REGEXP %s")
                    else:
                        conditions.append("metric_id REGEXP %s")
                    params.append("[^\.]%s=" % data['match_tag_equality'][0])
            elif 'match_tag_regex' in data:
                if data['negate']:
                    conditions.append("metric_id NOT REGEXP %s")
                else:
                    conditions.append("metric_id REGEXP %s")
                params.append("[^\.]%s=%s[\.$]" % data['match_tag_regex'])
            elif 'match_id_regex' in data:
                if data['negate']:
                    conditions.append("metric_id NOT REGEXP %s")
                else:
                    conditions.append("metric_id REGEXP %s")
                params.append(k)

        sql_query = "SELECT metric_id FROM metrics_tags AS mt JOIN tags AS t ON t.tag_id = mt.tag_id WHERE\n "
        sql_query += ' AND '.join(conditions)
        print "sql_query:", sql_query
        print "params:", params
        return (sql_query, params)

    def build_sql_query2(self, query):
        # option 2.
        wheres = []
        sub_wheres = []
        params = []
        for (k, data) in query.items():
            if 'match_tag_equality' in data:
                if data['match_tag_equality'][1]:
                    sub_wheres.append((data['negate'], "t.tag_key = %s AND t.tag_val = %s", data['match_tag_equality']))
                else:
                    sub_wheres.append((data['negate'], "t.tag_key = %s", (data['match_tag_equality'][0],)))
            elif 'match_tag_regex' in data:
                if self.regex_to_like(data['match_tag_regex'][1]):
                    data['match_tag_regex'][1] = '%%%s%%' % data['match_tag_regex'][1]
                    sub_wheres.append((data['negate'], "t.tag_key = %s AND t.tag_val LIKE %s", data['match_tag_regex']))
                else:
                    sub_wheres.append((data['negate'], "t.tag_key = %s AND t.tag_val REGEXP %s", data['match_tag_regex']))
            elif 'match_id_regex' in data:
                if data['negate']:
                    if self.regex_to_like(k):
                        wheres.append("metric_id NOT LIKE %s")
                        params.append("%%%s%%" % k)
                    else:
                        wheres.append("metric_id NOT REGEXP %s")
                        params.append(k)
                else:
                    if self.regex_to_like(k):
                        wheres.append("metric_id LIKE %s")
                        params.append("%%%s%%" % k)
                    else:
                        wheres.append("metric_id REGEXP %s")
                        params.append(k)
        for (negate, condition, param_list) in sub_wheres:
            condition = "select mt.metric_id from metrics_tags mt left join tags t on t.tag_id=mt.tag_id where %s" % condition
            if negate:
                condition = "metric_id NOT IN (%s)" % condition
            else:
                condition = "metric_id IN (%s)" % condition
            wheres.append(condition)
            params.extend(param_list)

        sql_query = "SELECT metrics_tags.metric_id, tags.tag_key, tags.tag_val FROM metrics_tags, tags WHERE metrics_tags.tag_id = tags.tag_id\nAND "
        sql_query += '\nAND '.join(wheres)
        print "sql_query:", sql_query
        print "params:", params
        return (sql_query, params)

    def build_sql_query3(self, query):
        # option 3. with regex: 21s, with LIKE 'foo' 8 seconds, with LIKE '%foo%' 14s
        # TODO join with actual tags
        # TODO regex_to_like optimisation
        wheres = []
        havings = []
        params = []
        for (k, data) in query.items():
            if 'match_tag_equality' in data:
                if data['match_tag_equality'][1]:
                    condition = ("t.tag_key = %s AND t.tag_val = %s", data['match_tag_equality'])
                else:
                    condition = ("t.tag_key = %s", (data['match_tag_equality'][0],))
            elif 'match_tag_regex' in data:
                condition = ("t.tag_key = %s AND t.tag_val REGEXP %s", data['match_tag_regex'])
            elif 'match_id_regex' in data:
                condition = ("metric_id REGEXP %s", (k,))
            wheres.append("(%s)" % condition[0])
            if data['negate']:
                havings.append("SUM(%s) = 0" % condition[0])
            else:
                havings.append("SUM(%s) > 0" % condition[0])
            params.extend(condition[1])

        sql_query = "SELECT metric_id FROM metrics_tags AS mt JOIN tags AS t ON t.tag_id = mt.tag_id WHERE\n "
        sql_query += ' OR '.join(wheres) + " GROUP BY metric_id HAVING\n "
        sql_query += ' AND '.join(havings)
        params.extend(params)
        print "sql_query:", sql_query
        print "params:", params
        return (sql_query, params)

    def matching(self, query):
        # this is very inefficient :(
        # future optimisation: query['limit_targets'] can be applied if no
        # sum_by or kind of later aggregation
        # TODO make sure all tag conditions are proper (what:, what=, etc)
        """
        query looks like so:
        {'patterns': ['target_type=', 'what=', '!tag_k=not_equals_thistag_v', 'tag_k:match_this_val', 'arbitrary', 'words']
        }
        after parsing:
        {
        'tag_k=not_equals_thistag_v': {'negate': True, 'match_tag_equality': ['tag_k', 'not_equals_thistag_v']},
        'target_type=':               {'negate': False, 'match_tag_equality': ['target_type', '']},
        'what=':                      {'negate': False, 'match_tag_equality': ['what', '']},
        'tag_k:match_this_val':       {'negate': False, 'match_tag_regex': ['tag_k', 'match_this_val']},
        'words':                      {'negate': False, 'match_id_regex': <_sre.SRE_Pattern object at 0x2612cb0>},
        'arbitrary':                  {'negate': False, 'match_id_regex': <_sre.SRE_Pattern object at 0x7f6cc000bd90>}
        }
        """
        query = parse_patterns(query)
        (sql_query, params) = self.build_sql_query1(query)
        self.db.execute(sql_query, params)
        return self.build_metrics(self.db.fetchall())

    def build_metrics(self, rows):
        results = {}
        for (metric_id, tag_key, tag_val) in rows:
            try:
                results[metric_id]['tags'][tag_key] = tag_val
            except KeyError:
                results[metric_id] = {
                    'graphite_metric': metric_id,
                    'tags': {
                        tag_key: tag_val
                    }
                }
        return results


def parse_patterns(query, graph=False):
    # prepare higher performing query structure
    # note that if you have twice the exact same "word" (ignoring leading '!'), the last one wins
    patterns = {}
    for pattern in query['patterns']:
        negate = False
        if pattern.startswith('!'):
            negate = True
            pattern = pattern[1:]
        patterns[pattern] = {'negate': negate}
        if '=' in pattern:
            if not graph or pattern not in ('target_type=', 'what='):
                patterns[pattern]['match_tag_equality'] = pattern.split('=')
            else:
                del patterns[pattern]
        elif ':' in pattern:
            if not graph or pattern not in ('target_type:', 'what:'):
                patterns[pattern]['match_tag_regex'] = pattern.split(':')
            else:
                del patterns[pattern]
        else:
            patterns[pattern]['match_id_regex'] = re.compile(pattern)
    return patterns
