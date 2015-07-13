#!/bin/bash
cd js/ &> /dev/null
[[ "$1" ]] && ver="$1" || ver=`date +%Y-%m-%d_%H.%M.%S`
# get file and save as main_VER_raw_SHA.js
curl -s http://agar.io/ | awk '/^\(function\(..?,..?\)\{/,/<\/script>/' | head -n -1 > main_${ver}_tmp.js
sha=`sha256sum main_${ver}_tmp.js | cut -d\  -f1`
mv main_${ver}_tmp.js main_${ver}_raw_${sha}.js
# the SHA of all file names is the one of the _raw file content
js-beautify <( tr -d '\n' < main_${ver}_raw_${sha}.js ) > main_${ver}_nice_${sha}.js
sed 's/\b[a-zA-Z]\{1,2\}\b/XX/g;s/$X*/XX/g' main_${ver}_nice_${sha}.js > main_${ver}_xx_${sha}.js
echo "$sha"

