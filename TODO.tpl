<ul>
    <li><a href="https://github.com/graphite-project/graphite-web/issues/103">graphite bug</a>
        breaking our graphs when using scale(), movingAverage() and maybe more, and when using function aliases like sum()</li>
    <li>a way to plot sums of matching targets. for example: disk sum(_srv) sum (!_srv) to show 2 plots</li>
    <li>number of put/delete requests arriving on swift proxy</li>
    <li>if graphite can't handle the syntax and the graphite http request errors out, show nice error boxes</li>
    <li>counters of number of objects, objects added/deleted per second (needs plugin for monitoring agent)</li>
    <li>swift dispersion report metrics over time</li>
    <li>order by graph_name DESC etc</li>
    <li>make sure that target types are properly named in all templates</li>
    <li>add rate type for disk usage increase/decrease by computing the derivative, also mention this feature in README</li>
    <li>disk io rates</li>
    <li>auto adjust height of graphs based on #targets. with many targets, the legends start to overlap</li>
    <li>a way to distribute this including deps directly for easy and reliable install</li>
    <li>allow updating metrics.json file from a dropdown menu when you hoover over 'last metrucs update'</li>
    <li>ajax refresh for 'last metrics update'</li>
    <li>maybe... under query, suggest tags, and even patterns (by going over metrics, stripping out all tags and listing what remains, uniqued)</li>
</ul>
