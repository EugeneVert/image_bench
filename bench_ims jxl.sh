#!/usr/bin/env bash

format="cjxl"
qualitys=""
# for ((j=5;j<=75;j+=5))
# do
#     qualitys=(${qualitys[@]} "$j")
# done
# for j in $(seq 70 1 90)
# do
#     qualitys=(${qualitys[@]} "$j")
# done
for j in $(seq 85 1 90)
do
    qualitys=(${qualitys[@]} "$j")
done
for j in $(seq 90.5 0.5 99.5)
do
    qualitys=(${qualitys[@]} "$j")
done

echo "qualitys:"
printf "%s " "${qualitys[@]}"
echo

cnt=${#qualitys[@]}
for ((i=0;i<cnt;i++)); do
    qualitys[i]="${format}:-q/_/${qualitys[i]} "
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
