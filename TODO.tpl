<ul>
    <li>fix date/time picker (plenty of plugins out there.. but I couldn't get it to work)</li>
    <li><a href="https://github.com/graphite-project/graphite-web/issues/103">graphite bug</a>
        breaking our graphs when using scale(), movingAverage() and maybe more, and when using function aliases like sum()</li>
    <li>a way to plot sums of matching targets. for example: disk sum(_srv) sum (!_srv) to show 2 plots</li>
    <li>number of put requests arriving on proxy</li>
    <li>counters of number of objects, objects added/deleted per second (needs plugin for monitoring agent)</li>
    <li>swift dispersion report metrics over time</li>
    <li>order by graph_name DESC etc</li>
    <li>add rate type for disk usage increase/decrease by computing the derivative, also mention this feature in README</li>
    <li>disk io rates</li>
    <li>auto adjust height of graphs based on #targets. with many targets, the legends start to overlap</li>
    <li>a way to distribute this including deps directly for easy and reliable install</li>
    <li>maybe... under query, suggest tags, and even patterns (by going over metrics, stripping out all tags and listing what remains, uniqued)</li>
</ul>
