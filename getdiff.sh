#!/bin/bash
cd js/ &> /dev/null

ver=`date +%Y-%m-%d_%H.%M.%S`
sha=`./getmain.sh "$ver"`

unset -v filepreprev
unset -v fileprev
for file in main_*_xx_*.js; do
  if [[ $file > $fileprev ]]; then
    filepreprev="$fileprev"
    fileprev="$file"
  fi
done
verpreprev=`<<<"$filepreprev" grep -Po '(?<=main_)[^_]*'`
verprev=`<<<"$fileprev" grep -Po '(?<=main_)[^_]*'`
shapreprev=`<<<"$filepreprev" grep -Po '[^_]*(?=\.js)'`
shaprev=`<<<"$fileprev" grep -Po '[^_]*(?=\.js)'`

echo "PrePrev  $verpreprev $shapreprev"
echo "Previous $verprev $shaprev"
echo "Current  $ver $sha"

if [[ $sha == $shaprev ]]; then
  echo "Same SHA"
  echo "$filepreprev $fileprev"
else
  echo "New SHA"
  echo "$fileprev main_${ver}_xx_${sha}.js"
fi

