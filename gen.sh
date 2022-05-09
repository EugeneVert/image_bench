#!/usr/bin/env bash

#              |codec   | out_dir   | args
./bench.py "avifenc" "avifenc"  "-a color\.enable-chroma-deltaq=1 -a color\.enable-qm=1 -a color\.deltaq-mode=3"
./bench.py "cjxl"    "jxl_s7"   "-e 7"
./bench.py "cjxl"    "jxl_s7np" "-e 7 --patches=0"
./bench.py "cavif"   "cavif"    "-s 6 -f -o"
# ./bench_ims.sh "cwebp"   "webp"     " -o"
