# Graph explorer

A highly interactive dashboard to satisfy varying ad-hoc information needs across a multitude of metrics in a very powerful way:  

* The core of graph-explorer is a database containing your metrics extended with tags
(key-value pairs that represent server, service, type, unit, ...)
* You can use expressive queries which leverage this metadata to filter targets, group them into graphs, process and aggregate them on the fly.
Something like SQL but metrics for rows and a list of graph definitions as a result set.  All graphs are built dynamically.

The graphs themselves support annotated events and are also interactive because it uses [timeserieswidget](https://github.com/vimeo/timeserieswidget)
Furthermore, the code is simple and hackable (just a few hundred sLOC) python code and is a breeze to get running

![Screenshot](https://raw.github.com/vimeo/graph-explorer/master/screenshot.png)

It also has a dashboards feature which are pages that show N queries along with their results (0-N graphs each).

## Screencast

explains most of the concepts and tricks in less than 30minutes.
[vimeo.com/67080202](http://vimeo.com/67080202)

## Structured Metrics

In graphite, a metric has a name and a corresponding time series of values.
Graph-explorer's metrics are structured: they contain key-value tags that describe all their attributes, the unit, the metric type, etc.
You can generate the tag database by using plugins that parse metrics using regular expressions, or by tagging them as they flow into graphite.
See the [Structured Metrics page](https://github.com/vimeo/graph-explorer/wiki/Structured-Metrics)


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
* any other pattern is treated as a regular expression and gets matched on the metric as well as tags.
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

### avg over `<timespec>`

instead of showing the metric directly, show the moving average.  
timespec looks like `[amount]unit`

* amount is a number, and defaults to 1
* unit is one of the [recognized time units](https://github.com/vimeo/graph-explorer/wiki/Units-&-Prefixes)

example: `avg over 30M` to show the moving average over 30 minutes.

note: the points up until the first datapoint where a full period is covered, are empty.
so by default `avg over 1d` shows nothing, so you need something like `avg over 1d from -2days`.

### Inline unit conversion

when you specify something like `unit=B/M` or `unit=B/h` it will automatically show the requested metric per the new
time interval, by rescaling B/s metrics appropriately.  Currently only supported for metrics that are per second.
Only looks at the divisor, not the dividend, and doesn't take prefixes into account. None of that is needed
because no-one ever uses 'ks' (kiloseconds) and the graphs automatically display appropriate prefixes (i.e. no need
to type 'TB/d' for a 'B/s' metric, just make it 'B/d', if it's in the terabyte range the graph will automatically show the
appropriate prefixes).  It follows that this only needs to be done for rates. For metrics that are not expressed per a time, this is
not needed as the automatic prefixes on the graph suffice.

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
* install elasticsearch and run it (super easy, see http://www.elasticsearch.org/guide/reference/setup/installation/, just set a unique cluster name)
* pytz for rawes(elasticsearch) (TODO: we can probably avoid this)

## Installation

Just get a code checkout and initialize all git submodules, like so:

```
git clone --recursive https://github.com/vimeo/graph-explorer.git
```
This will give you the latest bleeding edge code (master branch), which can be a buggy sometimes.
You can use a "release" by checking out one of the tags:

* 2013.06.13
* 2013.04.19

or of course, download a release from the [release page](https://github.com/vimeo/graph-explorer/releases)

## Configuration of graph-explorer

* edit config.py for basic config options.  If you want annotated events using [anthracite](https://github.com/Dieterbe/anthracite) set `anthracite_url`
* have a look at preferences.py, this is where you can configure timezone, targets colors, a few graph options, etc.
* [populate an elasticsearch database with structured metrics](https://github.com/vimeo/graph-explorer/wiki/Structured-Metrics)

## Configuration of graphite server

you'll need a small tweak to allow this app to request data from graphite.
For apache2 this works:

    Header set Access-Control-Allow-Origin "*"
    Header set Access-Control-Allow-Methods "GET, OPTIONS, POST"
    Header set Access-Control-Allow-Headers "origin, authorization, accept"

## Running

* default, with Paste (included):
`./graph-explorer.py` and your page is available at `<ip>:8080`

* alternatively, if you use gunicorn, you can run it with multi-workers like so:
`gunicorn -w 4 app:'default_app()' -b 0.0.0.0:8080`


## First steps

* go to the debug page and see if any of metrics are being recognized.  You'll see tables of all tags found across your targets. and below that all enhanced metrics found.
* if there's no metrics there, make sure you have a recent metrics.json file and plugins that have correct regular expressions that can match your metric names.  A good starting point is using statsd and a monitoring agent like diamond or collectd.
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

`backend.update_data()` loads your metrics and gets matching targets by calling `list_metrics(metrics)` on a structured_metrics object.
* `list_metrics` goes over every metric, and for each goes over every plugin (ordered by priority), and
  * calls `plugin_object.upgrade_metric(metric)`, which goes over all target configs in the plugin and tries each out.
  * each target config can have multiple match regexes. first one wins. (it gets created, sanitized, and the configure functions are run)
  * each target config for which none of the no_match regexes matches, or the limit is reached, doesn't get yielded.
  * first plugin that yields a proto2 metric wins for this metric (no other plugins are tried for that metric). that's why catchall plugins have lowest priority.


## Writing your own dashboards

Dashboards are simple html template files that display the results for one or more queries.  Just look at the existing files, create a new one,
and it will automatically be listed (after a graph-explorer restart)

## Getting in touch

* irc: #graph-explorer on freenode
* github issues for bugs, feature requests, questions, feedback
