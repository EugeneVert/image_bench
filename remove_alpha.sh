#!/usr/bin/env bash
cd "$1" || exit
for i in *.png; do
has_alpha=$(identify -format '%[channels]' "$i" | grep srgba)
if [[ "$has_alpha" ]]; then
    echo "$i"
    mkdir -p ./orig
    mv "$i" ./orig
    convert ./orig/"$i" -alpha off PNG24:"$i"
fi
done
