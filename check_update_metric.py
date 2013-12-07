#!/usr/bin/env python2
import os
import sys
from pprint import pprint

import structured_metrics

"""
this program shows how the proto1 -> proto2 upgrade looks like for
all metrics given as cmdline arguments.
very convenient to verify the working of plugins etc.
"""

os.chdir(os.path.dirname(os.path.abspath(__file__)))

s_metrics = structured_metrics.StructuredMetrics()
errors = s_metrics.load_plugins()
if len(errors) > 0:
    print 'errors encountered while loading plugins:'
    for e in errors:
        print '\t%s' % e
for v in s_metrics.list_metrics(sys.argv[1:]).values():
    pprint(v)
