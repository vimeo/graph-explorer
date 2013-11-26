#!/bin/bash

exclpats=$(grep '^[^#]' .lint_exclusions)

exclusions=( -name .git )
for exclpat in $exclpats; do exclusions+=( -o -path "./$exclpat" ); done

set -e

find . \( "${exclusions[@]}" \) -prune -o -name '*.py' -print0 \
    | xargs -0r pylint --rcfile=.pylintrc
#find . \( "${exclusions[@]}" \) -prune -o -name '*.py' -print0 \
#    | xargs -0r pep8
