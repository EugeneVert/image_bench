#!/usr/bin/env bash

format="$1"
out_dir="$2"
cmdargs="$3"

echo "qualitys:"
case "$format" in
    "cjxl" | "cwebp")
        # for ((j=5;j<=75;j+=5))
        # do
        #     qualitys=("${qualitys[@]}" "$j")
        # done
        for j in $(seq 65 2 85)
        do
            qualitys=("${qualitys[@]}" "$j")
        done
        for j in $(seq 86 1 90)
        do
            qualitys=("${qualitys[@]}" "$j")
        done
        for j in $(seq 90.5 0.5 99.5)
        do
            qualitys=("${qualitys[@]}" "$j")
        done
        printf "%s " "${qualitys[@]}"
        cnt=${#qualitys[@]}
        for ((i=0;i<cnt;i++)); do
            qualitys[i]="${format}:-q ${qualitys[i]}$cmdargs "
        done
        ;;
    "avif")
        for j in $(seq 2 2 32)
        do
            qualitys=("${qualitys[@]}" "$j")
        done
        printf "%s " "${qualitys[@]}"
        cnt=${#qualitys[@]}
        for ((i=0;i<cnt;i++)); do
            qualitys[i]="${format}:--min $((qualitys[i] - 2)) --max ${qualitys[i]}$cmdargs "
        done
        ;;
    *) echo "Avaible formats: cjxl, avif, cwepb"; exit
esac
echo

# output dir (--csv_path)
if [ ! -d ./"$out_dir"/ ]
then
   mkdir ./"$out_dir"/
fi

# run 'metric' for every file in image dir
cd ./images || exit
for i in ./* ; do
    i_ext=${i##*\.}
    i_is_image=$(grep -F -x "$i_ext" <<EOF
png
jpg
EOF
)
    if [[ ! "$i_is_image" ]]; then continue; fi
    ../metric --csv --metrics "$i" -c "${qualitys[@]}" --csv_path "../$out_dir/$i.csv"
done
cd ..

python ./average_csv_pd.py "./$out_dir"
