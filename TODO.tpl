<ul>
    <li><a href="https://github.com/graphite-project/graphite-web/issues/103">graphite bug</a>
        breaking our graphs when using scale(), movingAverage() and maybe more, and when using function aliases like sum()</li>
    <li>display tags properly (colored labels) in group by info, and other pages like debug, inspect</li>
    <li>automatically generate vtitles: show constants: what (current if gage, total if counter) type (/s if rate, /flushInterval if count) [on server]</li>
    <li>a way to plot sums of matching targets. for example: disk sum(_srv) sum (!_srv) to show 2 plots. or by extension: any graphite function</li>
    <li>allow "or" style matches across groups of patterns,like so: cpu iowait dfs || plugin=udp dfs1. maybe this can be integrated with the above</li>
    <li>number of put/delete requests arriving on swift proxy</li>
    <li>if graphite can't handle the syntax and the graphite http request errors out, show nice error boxes</li>
    <li>counters of number of objects, objects added/deleted per second (needs plugin for monitoring agent)</li>
    <li>order by graph_name DESC etc</li>
    <li>make sure that target types are properly named in all plugins</li>
    <li>simplify tags semantics: only have tags when they matched something. then we can probably remove some stuff from the language syntax</li>
    <li>filestat: display percentage as assigned/max ? same idea for disk used and others. maybe a new generic target type thing</li>
    <li>based on target_type, set graph vtitle (unless overridden by plugin, but you should have a good reason to do so)</li>
    <li>maybe: query syntax: 'in G' 'in M' to divide by 10^9/10^6. or actually.. this is too graph-specific. graphs should automatically do this</li>
    <li>auto adjust height of graphs based on #targets. with many targets, the legends start to overlap</li>
    <li>a way to distribute this including deps directly for easy and reliable install</li>
    <li>filter by expression (graphite function(s) or simplified). example: "where movingAverage(10h) &gt; 100" </li>
    <li>allow updating metrics.json file from a dropdown menu when you hoover over 'last metrucs update'</li>
    <li>ajax refresh for 'last metrics update'</li>
    <li>plugin for http://obfuscurity.com/2012/06/Watching-the-Carbon-Feed</li>
    <li>allow plugins to yield targets without corresponding to particular metrics. i.e. for statsd this is useful:
    sum(stats.timers.*.count,stats.timers.*.*.count,stats.timers.*.*.*.count,stats.timers.*.*.*.*.count,stats.timers.*.*.*.*.*.count)
    </li>
    <li>maybe... under query, suggest tags, and even patterns (by going over metrics, stripping out all tags and listing what remains, uniqued)</li>
</ul>
