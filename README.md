# Graph explorer

A highly interactive dashboard to satisfy varying ad-hoc information needs across a multitude of metrics by using plugins which

* add metadata to individual graphite metrics, (tags such as as server, service, type, ...)
* define how to generate (multiple) targets for any metric (to render as a count, a rate, etc)

you can then use expressive queries which leverage this metadata to filter targets and group them into graphs in arbitrary ways.
Something like SQL but targets for rows and a list of graph definitions as a result set.
The graphs themselves support annotated events and are also interactive because it uses [timeserieswidget](https://github.com/vimeo/timeserieswidget)

Furthermore, the code is simple and hackable (just a few hundred sLOC), uses simple python files as plugins, and is a breeze to get running (only external dep. is python)

![Screenshot](https://raw.github.com/vimeo/graph-explorer/master/screenshot.png)

## Screencast

explains most of the concepts and tricks in less than 30minutes.
[vimeo.com/67080202](http://vimeo.com/67080202)

## Enhanced Metrics

In graphite, a metric has a name and a corresponding time series of values.
Graph-explorer's plugins define rules which match metric names, parse them and yield a target with associated metadata:

* tags from fields in the metric name (server, service, interface_name, etc) by using named groups in a regex.  (there's some guidelines for tags, see below)
* target_type (count, rate, gauge, ...)
* unit (MB, queries/s, ...)
* plugin (i.e. 'cpu')
* the graphite target (often just the metric name, but you can use the [graphite functions](http://graphite.readthedocs.org/en/1.0/functions.html) like `derivative`, `scale()` etc.

all metadata is made available as a tag, and an id is generated from all tag keys and values, to provide easy matching.

the configuration also provide settings:

* `configure` function or list of functions to further enhance the target dynamically (given the match object and the target along with its config), in addition to the default
  defined function which can also be overridden.

Note that it is trivial to yield multiple targets from the same metric.  I.e. you can have a metric available as rate, counter, average, etc by applying different functions.

Try to use standardized nomenclature in target types and tags.  Do pretty much what statsd does:

* rate: a number per second
* count: a number per a given interval (such as a statsd flushInterval)
* gauge: values at each point in time
* counter: a number that keeps increasing over time (but might wrap/reset at some points) (no statsd counterpart) (you'll probably also want to yield this as a rate with `derivative()`)
* timing: TBD

other words you might use are `pct` (percent), `http_method`, `device`, etc.  Also, keep everything in lowercase, that just keeps things easy when matching.
Some exceptions for things that are accepted to be upper case are http methods (GET, PUT,etc)

tag definitions:
"what": the intrinsic thing that we're graphing (not *how* we graph it). i.e. errors, requests, cpu_state (used in vtitle, grouping into graphs)
"type": extra info. i.e. if what is errors, this can be 'in'. if what is requests, this can be '404'. sometimes you may want to put multiple words here, and that's ok (but consider creating new tags for those)
"wt": often a metric path will contain one key that has info on both the "what" and "type", "wt" is commonly used to catch it, so you can sanitize it (see below)

all metrics must have a unit tag. because otherwise they are meaningless, also because they are used in the default group_by

sanitization
the process of properly setting "what" and "type" tags from a "wt" tag and deleting the "wt" tag again.

## Graphs

* Are dynamically built as requested by your query.


## Query parsing and execution

the Graphite Query Language is a language designed to:

* let you compose graphs from metrics in a flexible way.
  you can use tags and pattern matching to filter and group targets (from different plugins) into the same or nearby graphs for easy comparison and correlation across seamingly different aspects.
  you can compare metrics, the rate at which the metrics change, etc.
* get in your way as little as possible (loose syntax that's easy to start with but provides powerfull features)


## the algorithm

* from the query input you provide...
* parse out any special statements (see below)
* split up result into separate patterns (white space as boundary), each of which must match on its own.
* you can use `!` to negate
* any pattern that has `:` or `=` inside it matches on tags, like so:
  * `=<val>`      : a tag must have value `<val>`
  * `<key>=`      : a tag with key `<key>` must exist
  * `<key>=<val>` : a tag with key `<key>` must exist and have value `<val>`
  * `:<val>`      : a tag with value matching regex `<val>` must exist
  * `<key>:`      : a tag with key matching regex `<key>` must exist
  * `<key>:<val>` : a tag with key `<key>` must exist and its value must match the regex `<val>`
* any other pattern is treated as a regular expression, which must match the target name.
* matching targets are collected, grouped into graphs and rendered

note:

* order between patterns is irrelevant
* tag matching for 'target_type' and 'what' tags are not performed on graph objects, because they don't apply for them.

## special predicates

Unless mentioned otherwise, these statements are all optional (i.e. have default values), can occur anywhere within the query and
the values must not contain white space.

### `graph|list `

default: graph  
this statement goes in the beginning of the query.

* graph (default): builds and shows the graphs from your input
* list: shows all matching targets (not the matching graphs)


### group by `<tagspec>` and GROUP BY `<tagspec>`

`<tagspec>` is a list like so: `foo[=][,bar[=][,baz[=][...]]]`
basically a comma-separated list of tags with optional '=' suffix to denote soft or hard (see below).

by default, grouping is by `unit=` and `server`.
The tags `unit` is strong, meaning a `<tag>=` pattern is added to the query so that only targets are shown that have the tag.
The tag `server` is soft so that no pattern is added, and targets without this tag will show up too.

You can affect this in two ways:
* specify `group by <tagspec>` to keep the standard hard tags and replace all soft tags with `foo`, `bar`, etc.
* specify `GROUP BY <tagspec>` to replace the original list entirely and only group by `foo`, `bar`, etc.

For example, the cpu plugin yields targets with tags:

* target_type: gauge_pct (all of them)
* what: cpu_state (all of them)
* type : something like iowait
* server: the host name
* core: core name (core0, etc)

* default: grouping by `target_type=`, `what=` and `server`.  So you get a graph for each server, showing the different types for all different cores.
* `group by type` shows for each type (iowait, idle, etc) a graph comparing all cores on all servers
* `group by core,server` shows a graph for each core on each server.

(a good way to try this out would be to query for `cpu_state` and maybe filter on servername so you only get a few hostnames)
(no effect in 'list' mode)


### sum by `<tagspec>`

`<tagspec>` is a list like so: `foo[,bar][...]`

causes all the targets on every graph to be summed together by these tags, and shown as one.  if their other tags have the same values.
(no effect in 'list' mode)


### from `<word>`

default: '-24hours'.  
accepts anything [graphite accepts](http://graphite.readthedocs.org/en/1.0/url-api.html#from-until) which is a whole lot
(no effect in 'list' mode)

### to `<word>`

default: 'now'.  
accepts anything graphite accepts (see above)
(no effect in 'list' mode)


### limit `<number>`

default: 500
limit returned targets (to avoid killing you browser and/or graphite server). 0 means no limit
(no effect in 'list' mode)

## Examples

* `cpu`: all cpu graphs (for all machines)
* `web cpu`: cpu graphs for all servers matching 'web'. (grouped by server by default)
* `web cpu total.(system|idle|user|iowait)`: restrict to some common cpu metrics
* `web cpu total.(system|idle|user|iowait) group by type`: same, but compare matching servers on a graph for each cpu metric
* `web123`: all graphs of web123
* `server[1-5] (mem|cpu)`: memory and cpu graphs of servers 1 through 5
* `!server[1-5] (mem|cpu) from 20091201 to 20091231`: memory and cpu graphs of all servers, except servers 1 through 5. the entire month December
* `targets dfs1 from noon+yesterday`: see all targets available for server dfs1
* `diskspace_count type=byte_used mountpoint:_srv server:foo`: compare bytes used across all mountpoints matching '/srv' on all servers matching 'foo'.
* `diskspace_rate type=byte_used mountpoint:_srv server:foo group by type`: similar, but compare the rate of change, and show graphs for each type (`bytes_free`, `inodes_used`, etc) so you can compare each server and/mountpoint.


## Display of graphs:

* all tags are displayed in a label whose color is deterministically computed from the name of the tag; they are also always printed in a consistent order
  so that it's easy to discern what's what, and consistent throughout the entire app.
* all tags that are constant for a graph (due to grouping by them, or because retrieved targets happen to share the same tag values) are shown as the graph title
* the vertical title shows more info about the `<what>`, `<type>` and `<target_type>` in a more humanly readble form ("/s" for rate, "/<interval>" for counts, etc.
* all tags that are variable across targets in a graph are shown as labels in the target legend. click on them to get more info about the metric (graphite metric name, found tags, etc)
* in preferences.py you can define your count interval (statsd flushInterval) and graph options so that you can for example use binary prefixes instead of SI for diskspace/memory graphs;
 stacked graphs when displaying cpu states, etc.


## Dependencies

* python2: either 2.6 or higher, or 2.5 and the additional simplejson module
* mysql-python (MySQL-python on centos)
* a working mysql database (that contains the metrics. i.e. can be the same as your carbon-tagger db)

## Installation

Just get a code checkout and initialize all git submodules, like so:

```
git clone --recursive https://github.com/vimeo/graph-explorer.git
```
This will give you the latest bleeding edge code (master branch), which can be a buggy sometimes.
You can use a "release" by checking out one of the tags:

* 2013.06.13
  * moved static graph defs (for those who use em) from structured metrics in to separate graph plugins
  * add experimental shortcut functions for easier defining targets
  * add `sum by` support
  * better support for multiple (gunicorn or other) workers
  * perf tweak: compute structured metrics in a separate process that builds cache files which the app just reloads
* 2013.04.19
  * first stable release


## Configuration of graph-explorer

```
# inside the graph-explorer directory
$EDITOR config.py
# if you want annotated events using [anthracite](https://github.com/Dieterbe/anthracite) set `anthracite_url`
# run update_metrics.py (protip: use cron), this downloads metrics.json and builds the enhanced metrics (tag datastructures).
*/20 * * * * /path/to/graph-explorer/update_metrics.py &>/dev/null
(note, if you have a lot of metrics, this can take a while. takes 50minutes on my 120k metrics. there's some low hanging optimisation fruit there though)
```

## Configuration of graphite server

you'll need a small tweak to allow this app to request data from graphite.
For apache2 this works:

    Header set Access-Control-Allow-Origin "*"
    Header set Access-Control-Allow-Methods "GET, OPTIONS"
    Header set Access-Control-Allow-Headers "origin, authorization, accept"

## Running

* default, with Paste (included):
`./graph-explorer.py` and your page is available at `<ip>:8080`

* alternatively, if you use gunicorn, you can run it with multi-workers like so:
`gunicorn -w 4 app:'default_app()' -b 0.0.0.0:8080`


## First steps

* go to the debug page and see if any of metrics are being recognized.  You'll see tables of all tags found across your targets. and below that all enhanced metrics found.
* if there's no metrics there, make sure you have a recent metrics.json file and plugins that have correct regular expressions that can match your metric names.  A good starting point is using statsd and the diamond monitoring agent.
* start with a simple query like the name of a plugin or something you're sure will match something. example 'statsd' or 'plugin=statsd' or 'statsd count' etc.  the graph names and target names give you clues on other words you can use to filter.


## Troubleshooting

* no graphs show up and I don't know why.

first check in the top section if there are target matching and 'total graphs' is > 0.  
if not, your query expression might be too restricting.  or maybe it didn't find your metrics from metrics.json (see 'targets matching: x/total')  
if yes, check for any errors in the javascript console, (in firefox you need firebug, in chrome and such 'tools->javascript console')

also check all network requests in the network tab, and make sure they return http 200 or 304
especially, check that the http requests to `graphite/render/?<...>` return actual data.
(if not, there's something wrong with the request uri/targets.  you may be suffering from [this graphite bug](https://github.com/graphite-project/graphite-web/issues/289))

* i get some error wrt graphite/apache cors access restriction

see section 'Configuration of graphite server' above


## Writing your own plugins

Definitely read 'Enhanced Metrics' above, and preferrably the entire readme.
A simple plugin such as diskspace.py is a good starting point.
Notice:

* targets is a list of rules (and 'subrules' under the 'targets' key which inherit from their parent)
* the match regex must match a metric for it to yield an enhanced metric, all named groups will become tags
* target_type must be one of the predefined values (see above)
* one or more configurations can be applied, or override `default_configure_target` which always gets called
  in these functions you can return a dict which'll get merged into your target (or just alter the target directly).
  use this to change tags, the target, etc.

`backend.update_data()` loads your metrics and gets matching targets by calling `list_targets(metrics)` on a structured_metrics object.
* `list_targets` goes over every metric, and for each goes over every plugin (ordered by priority), and
  * calls `plugin_object.find_targets(metric)`, which goes over all target configs in the plugin and tries each out.
  * each target config can have multiple match regexes. each can yield a target. (it gets created, sanitized, and the configure functions are run)
  * each target config for which none of the no_match regexes matches, or the limit is reached, doesn't get yielded.
  * first plugin that yields one or more targets wins for this metric (no other plugins are tried for that metric). that's why catchall plugins have lowest priority.


## Getting in touch

* irc: #monitoringlove on freenode (I'm there, Dieterbe)
* or use github issues for bugs, feature requests, questions, feedback
