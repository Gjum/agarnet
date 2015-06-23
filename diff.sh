#!/bin/bash
cd js/ &> /dev/null
colordiff --ignore-space-change --ignore-blank-lines --side-by-side --speed-large-files --suppress-common-lines `./getdiff.sh | tail -n 1`
