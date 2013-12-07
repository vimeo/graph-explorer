<ul>
    <li>remove statically configured "suggested queries" (or make it an optional module). instead, track last_use and times_used of each query (after ordering), and show popular queries based on frecency. and/or allow saving queries with manual notes</li>
    <li>define how to generate (multiple) targets for any metric (to render as a count, a rate, etc)</li>
    <li>allow "or" style matches across groups of patterns,like so: cpu iowait dfs || plugin=udp dfs1. maybe this can be integrated with the above</li>
    <li>on graphs and inspect view, point to unit information in text, maybe wiki page</li>
    <li>some kind of UI feature that suggests tags keys/vals, to make it easier for newbies. in list and graph mode, and whether or not we already have a query</li>
    <li>fix what/type/target_type for timers in all plugins (already done in catchall_statsd)</li>
    monitor swift in/out speeds instead of timings
    <li>"global" rules to set extra tags-> everything with server:df.* -> tag env=prod-df, allows user to search on 'env' tag</li>
    <li>group by scale automatically: if things differ by orders of magnitude, put them on different graphs</li>
    <li>if graphite can't handle the syntax and the graphite http request errors out, show nice error boxes</li>
    <li>order by graph_name DESC etc</li>
    <li>histograms will be better (see http://localhost:8080/index/bin_%20group%20by%20type) after: 1) don't display empty tags in title 2) fix target colors</li>
    <li>filestat: display percentage as assigned/max ? same idea for disk used and others. maybe a new generic target type thing</li>
    <li>auto adjust height of graphs based on #targets. with many targets, the legends start to overlap</li>
    <li>filter by expression (graphite function(s) or simplified). example: "where movingAverage(10h) &gt; 100" </li>
    <li>update B/s in vtitle and constants if we're doing unit conversion like unit=B/d</li>
    <li>maybe... under query, suggest tags, and even patterns (by going over metrics, stripping out all tags and listing what remains, uniqued). or leverage ES facets</li>
</ul>
Ponderings:
<ul>
<li>load plugin has stored 5/15M averages, use those when user does 'avg over 5M or 15M'? 
</li>
<li>interactively dragging targets from one graph to another</li>
<li>interactive slider akin to 'avg over' (rickshaw has this)</li>
</ul>
