# Structured metrics

the graphite metric space is a flat tree, which is hard/troublesome to organize, and restrictive when searching/querying/grouping (for) metrics  

`structured_metrics` is a lightweight python library that uses plugins to read in a list of metric names and convert it into a multi-dimensional tag space.

per metric, one or more "enhanced targets" are yielded by:

* parsing out nodes (the things between dots) from the name and creating tags from them (using a regex with named groups)
* adding arbitrary metadata (tags)
* cleaning and standardizing tags (every target should have a clear `target_type` (gauge, count, ...) and a `what` (milliseconds, bytes, errors, ...) tag.


* you can yield multiple targets with different settings (for example a `counter` which just points to the graphite target,
and a `rate` with applies the `derivative` function, averaged out versions, views across different metrics, etc.)
* you can also apply further configuration, for example setting default colors (i.e. errors in red, cpu idle in green, ...)

This way you can make your metrics structured, clearly defined, avoid the organisation problem, have much more freedom for searching/querying, and show arbitrary metadata in the graphing phase.

`structured_metrics` comes with a bunch of plugins (for the diamond monitoring agent, statsd, openstack swift),
including fallback plugins that just assign node tags like n1, n2, n3, etc so you always have all your metrics available from the start.

