#!/bin/bash
cd js/ &> /dev/null
ver="$1"
curl -# http://agar.io/main_out.js?${ver} > main_${ver}_raw.js
js-beautify <( tr -d '\n' < main_${ver}_raw.js ) > main_${ver}_nice.js
sed 's/\b[a-zA-Z]\{1,2\}\b/XX/g;s/$XX*/XX/g' main_${ver}_nice.js > main_${ver}_xx.js

