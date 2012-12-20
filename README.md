# Graph explorer

A highly interactive dashboard to satisfy varying ad-hoc information needs across a multitude of metrics by using templates which

* add metadata to individual graphite metrics, (tags such as as server, service, type, ...)
* define how to generate (multiple) targets for any metric (to render as a count, a rate, etc)

you can then use expressive queries which leverage this metadata to filter targets and group them into graphs in arbitrary ways.
Something like SQL but targets for rows and a list of graph definitions as a result set.
The graphs themselves are also interactive and can be toggled between stacked/lines mode, more features (like toggling and reordering of targets, realtime zooming/panning) are on the way.

Quick example videos which are dated but give you an idea:

* [diskspace example (1:20)](https://vimeo.com/54906914)
* [openstack swift example (1:57)](https://vimeo.com/54912886)

Furthermore, the code is simple and hackable (just a few hundred sLOC), uses simple python files as templates, and is a breeze to get running (only external dep. is python)

![Screenshot](https://raw.github.com/Dieterbe/graph-explorer/master/screenshot.png)

## Enhanced Metrics

In graphite, a metric has a name and a corresponding time series of values.
Graph-explorer's templates have `target_type` settings which parse the metric names on which they apply and add metadata to them:

* tags from fields in the metric name (server, service, interface_name, etc) by using named groups in a regex.  
  usually the last field of a metric is called `type`.  (for example `iowait` or `upper_90` for statsd timers)
* target_type (count, rate, gauge, ...)
* class_name (cpu_state_percent etc)
* the graphite target (often just the metric name, but you can use the [graphite functions](http://graphite.readthedocs.org/en/1.0/functions.html) like `derivative`, `scale()` etc.

all metadata is made available as a tag, and an id is generated from all tag keys and values, to provide easy matching.

target_types also provide settings:

* `default_group_by` (usually `server`)
* `default_graph_options` which specify how to render these types by default

Note that it is trivial to yield multiple targets from the same metric.  I.e. you can have a metric available as rate, counter, average, etc by applying different functions.

Try to use standardized nomenclature in target types and tags.  Do pretty much what statsd does:

* rate: a number per second
* count: a number per a given interval (such as a statsd flushInterval)
* gauge: values at each point in time
* counter: a number that keeps increasing over time (but might wrap/reset at some points) (no statsd counterpart) (you'll probably also want to yield this as a rate with `derivative()`)
* timing: TBD

other words you might use are `pct` (percent), `http_method`, `device`, etc.  Also, keep everything in lowercase, that just keeps things easy when matching.
Some exceptions for things that are accepted to be upper case are http methods (GET, PUT,etc)

## Graphs

* Are built as requested by your query.
* Templates can yield graphs directly, they specify targets either as graphite strings or as config dict.  To be revised.  leverage enhanced targets?  Not sure how this will fit in
  as I'm aiming to make it possible to match metrics in a lightweight way and compose graphs ad-hoc with minimal fuss.  
  Note that graphs are matched in the same way targets are (based on their id, tags, etc)
  At this time only one example: in the statsd plugin


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

## special predicates

These statements are all optional (i.e. have default values) and can occur anywhere within the query.
Unless mentioned otherwise, the values must not contain white space.

### group by `<tag>`

default grouping is always at least by target_type, and secondary by what the `target_type`'s `default_group_by` (usually server), or by the tag you specified with this predicate.
a `:<tag>` pattern is implicitly added.

For example, the cpu template yields targets with tags:

* target_type: cpu_state_pct
* type : something like iowait
* server: hostname

it has default_group_by set to `server`  
You'll always have graphs with no other target_types than cpu metrics,
but additional grouping by:

* server shows a graph for each server listing all cpu states for that server.
* type yields a graph for each cpu state (sys, idle, iowait, etc) listing all servers.

This of course extends to >2 tags.

### from `<word>`

default: '-24hours'.  
accepts anything [graphite accepts](http://graphite.readthedocs.org/en/1.0/url-api.html#from-until) which is a whole lot

### to `<word>`

default: 'now'.  
accepts anything graphite accepts (see above)

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


## Dependencies

* python2

## Installation

```
git clone https://github.com/Dieterbe/graph-explorer.git
cd graph-explorer
git submodule update --init
cd graphitejs
git submodule update --init
```

## Configuration of graph-explorer

```
# inside the graph-explorer directory
$EDITOR config.py
# get metrics.json from your graphite server
source config.py && curl $graphite_url/metrics/index.json > metrics.json
# or better, put the included script in cron:
*/20 * * * * /path/to/graph-explorer/update_metrics.sh >/dev/null
```

## Configuration of graphite server

you'll need a small tweak to allow this app to request data from graphite. (we could use jsonp, but see https://github.com/obfuscurity/tasseo/pull/27)
For apache2 this works:

    Header set Access-Control-Allow-Origin "*"
    Header set Access-Control-Allow-Methods "GET, OPTIONS"
    Header set Access-Control-Allow-Headers "origin, authorization, accept"

## Running

`./graph-explorer.py` and your page is available at `<ip>:8080`

