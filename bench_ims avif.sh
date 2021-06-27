#!/usr/bin/env bash

format="avif"
qualitys=""
for j in $(seq 2 1 23)
do
    qualitys=(${qualitys[@]} "$j")
done

echo "qualitys:"
printf "%s " "${qualitys[@]}"
echo

cnt=${#qualitys[@]}
for ((i=0;i<cnt;i++)); do
    qualitys[i]="${format}:-s/_/6/_/--min/_/$((${qualitys[i]} - 2))/_/--max/_/${qualitys[i]}/_/-a/_/end-usage=q/_/-a/_/color:enable-chroma-deltaq=1 "  # /_/-a/_/tune=butteraugli
done

bench() {
    echo "$(dirname "$0")"/metric --csv --metrics "$1" -c ${qualitys[@]} --csv_path "$2"
}

if [ ! -d ./"$format" ]
then
   mkdir ./"$format"
fi

for i in *.png
do
    echo $(bench "$i" "./"$format"/"$i".csv")
    $(bench "$i" "./"$format"/"$i".csv")
done
