# Graph explorer

A highly interactive dashboard to satisfy varying ad-hoc information needs across a multitude of metrics by using templates which

* add metadata to invidual graphite metrics, (tags such as as server, service, type, ...)
* let you optionally define rules how to render any metric in multiple ways (as a count, a rate, etc)

you can then use expressive queries which leverage this metadata to filter targets and group them into graphs in arbitrary ways.
The graphs themselves are also interactive and can be toggled between stacked/lines mode, more features (like toggling and reordering of targets, realtime zooming/panning) are on the way.

Quick example videos which give you an idea:

* [diskspace example (1:20)](https://vimeo.com/54906914)
* [openstack swift example (1:57)](https://vimeo.com/54912886)

Furthermore, the code is simple and hackable (just a few hundred sLOC), uses simple python files as templates, and is a breeze to get running (only external dep. is python)

![Screenshot](https://raw.github.com/Dieterbe/graph-explorer/master/screenshot.png)

## The mechanism explained

* from a list of all metrics available in your graphite system (you can just download this from graphite box, see further down)
* a bunch of small template files which are fed this list and yield
  * enriched targets (by matching graphite metrics, assigning tags, and defining how to render them, each of these configs is a 'target_type'). target_types can also specify default graph options for entire graphs.
    targets are given an extensive name which includes all metadata.
  * graphs (this will be revised later. i think i'll want to yield graphs from the enriched targets instead of fram graphite metrics themselves)
* an input query provided by the user which filters targets and optionally defines how to group them (default grouping is always at least by target_type, and usually secondary by server)
* the graphs are shown.  All graphs are given clear names that are suitable for easy filtering.

## target_types

try to use some standardized nomenclature in target types and tags (named groups in the regex)
different target types for timing, counter rate, counter totals;
so for each metric regex, there's a target type. this is meant to work great with statsd
words you might use: state, type, pct, rate, count, timing, http_method.
note that you can create new target_types based on the same metrics in graphite, but by using
graphite functions such as derivative and integral

* type is usually just the last thing in the metric. for example `iowait` or `upper_90` for statsd timers
groupnames in regex automatically become tags in your targets.

## Query parsing and execution

## the algorithm

* from the query input you provide...
* parse out the (optional) `group by <tag>` (can occur anywhere. `<tag>` must not contain whitespace, a `:<tag>` pattern is implicitly added (see below))
* split up result into separate patterns (whitespace as boundary), each of which must match on its own.
* each pattern should be in lowercase
* you can use `!` to negate
* any pattern that has `:` inside it matches on tags, like so:
  * `:<foo>`      : a tag must have value `<foo>`
  * `<foo>:`      : a tag with key `<foo>` must exist
  * `<foo>:<bar>` : a tag with key `<foo>` must exist and have value `<bar>`
* any other pattern is treated as a regular expression, which must match the target name.
* matching targets are collected and grouped into graphs based on group settings (see below), and rendered

note:

* order between patterns is irrelevant
* if the pattern doesn't contain a "graph type specifier" like 'tpl' or 'targets', GE automatically filters on only 'targets', which is the recommended behavior.

## special statements

### group by `<tag>`

Graph targets are grouped by target_type, and additionally by the default_group_by of the target_type or any tag you specify with `group by <tag>`

For example, the cpu template yields targets with tags:

* target_type: cpu_state_pct
* type : something like iowait
* server: hostname

it has default_group_by set to `server`

You'll always have graphs with no other target_types than cpu metrics,
but additional grouping by:

* type yields a graph for each cpu state (sys, idle, iowait, etc) listing all servers.
* server shows a graph for each server listing all cpu states for that server.

This of course extends to >2 tags.

## Examples

* `cpu`: all cpu graphs (for all machines)
* `web cpu`: cpu graphs for all servers matching 'web'. (grouped by server by default)
* `web cpu total.(system|idle|user|iowait)`: restrict to some common cpu metrics
* `web cpu total.(system|idle|user|iowait) group by type`: same, but compare matching servers on a graph for each cpu metric
* `web123`: all graphs of web123
* `server[1-5] (mem|cpu)`: memory and cpu graphs of servers 1 through 5
* `!server[1-5] (mem|cpu)`: memory and cpu graphs of all servers, except servers 1 through 5
* `targets dfs1`: see all targets available for server dfs1

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

* cd graph-explorer
* make sure you have a list of your metrics in json format, you can easily get it like so:

    source config.py
    curl $graphite_url/metrics/index.json > metrics.json

* $EDITOR config.py

## Configuration of graphite server

you'll need a small tweak to allow this app to request data from graphite. (we could use jsonp, but see https://github.com/obfuscurity/tasseo/pull/27)
For apache2 this works:

    Header set Access-Control-Allow-Origin "*"
    Header set Access-Control-Allow-Methods "GET, OPTIONS"
    Header set Access-Control-Allow-Headers "origin, authorization, accept"

## Running

`./graph-explorer.py` and your page is available at `<ip>:8080`

