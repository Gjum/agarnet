#!/bin/bash
cd js/ &> /dev/null
meld `./getdiff.sh | tail -n 1` &

