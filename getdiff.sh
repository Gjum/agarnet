#!/bin/bash
cd js/ &> /dev/null
ver=`./getver.sh`

unset -v preprev
unset -v prev
for file in main_*_raw.js; do
  [[ $file > $prev ]] && preprev="$prev" && prev="$file"
done
preprev=`<<<"$preprev" grep -Po '(?<=main_)[^_]*'`
prev=`<<<"$prev" grep -Po '(?<=main_)[^_]*'`

echo "Previous versions were $preprev and $prev"

if [[ $ver == $prev ]]; then
  echo "Newest version is still $ver"
  echo "main_${preprev}_xx.js main_${ver}_xx.js"
  exit 0
fi

echo "Downloading version $ver"
./getmain.sh "$ver" 2>&1

echo "main_${prev}_xx.js main_${ver}_xx.js"

