# Graph explorer

## Design goals

A highly interactive dashboard to satisfy ad-hoc information needs across many similar metrics and graphs
using mainly expressive queries as input.

Plenty of dashboards provide statically configured pages for realtime and/or historic dashboards,
others provide some dynamism but are often hard to navigate and too restrictive when trying to find and correllate time-series data.

This tool aims to:

* show you the information you're looking for as quickly as possible, and with minimal cruft
* let you rearrange contents of graphs and more interactive features like realtime zooming, panning, legend reordering, etc
* diverge from the graphite API as little as possible. (no custom DSL like with gdash)
* use expressive queries to navigate and manipulate display of individual graphite targets as well as complete graphs generated from templates
* use simple version-controllable and editable plaintext files, avoid databases
* be simple as possible to get running from scratch.  No *just use sinatra* `sudo gem install crap loadError && wget http://make-a-mess.sh | sudo bash -c ; passenger needs gcc to recompile nginx; **loadError**`

![Screenshot](https://raw.github.com/Dieterbe/graph-explorer/master/screenshot.png)

# Interactive queries

Given:

* a list of all metrics available in your graphite system (you can just download this from graphite box)
* a bunch of small template files which define which graphs can be generated based on the available metrics you have, as well as individual targets which may be interesting by themselves (and for each target one or more tags; which you can use to categorize by server, by service, etc)
* an input query provided by the user

Graph-explorer will filter out all graphs as well as individual targets that match the query.  the targets are then grouped by a tag (given by user or from a default config) and yield one or more additional graphs.  All graphs are given clear names that are suitable for easy filtering.

** the plan is to make the target system more clever so that it automatically knows *how* to display the graph, thereby allowing us to completely remove the graphs as defined by the templates mechanism, and only work from tags and clever tags and context-awareness **

Pattern matching algorithm:

* Graph targets are grouped by target_type, and additionally by the default_group_by of the target_type or any tag you specify with `group by <tag>`
  For example, the cpu template yields targets with tags type something like 'iowait' and server:<servername> and all with target_type 'cpu'.  You'll always have graphs with no other target_types then cpu metrics, but additional
  grouping by type yields a graph for each cpu metric type (sys, idle, iowait, etc) listing all servers. grouping by server shows a graph for each server listing all cpu metrics for that server.
* Once the optional `group by <tag>` is removed, each word is treated as a separate regular expression, which must each seperately match.  so order between "match words" becomes irrelevant,
  you can keep everything lowercase. you can also use '!' to negate.
* if the pattern doesn't contain a "graph type specifier" like 'tpl' or 'targets',
  we assume you only want tpl ones. so GE adds 'tpl' so you only see templated graphs by default.

Examples:

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

* git clone graph-explorer
* git submodule init; git submodule update
* cd graphitejs; git submodule init; git submodule update

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

