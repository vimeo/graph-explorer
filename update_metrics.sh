#!/bin/bash -e
dir=$(dirname "$0")
cd "$dir"
source config.py
curl -s "$graphite_url/metrics/index.json" > metrics.json.tmp
mv metrics.json.tmp metrics.json
