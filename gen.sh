#!/usr/bin/env bash

#              |codec   | out_dir   | args
./bench_ims.sh "avif"   "avif"      " -a end-usage=q -a color:enable-chroma-deltaq=1"
./bench_ims.sh "cjxl"   "jxl_s7"    " -s 7"
./bench_ims.sh "cjxl"   "jxl_s8"    " -s 8"
./bench_ims.sh "cjxl"   "jxl_s9"    " -s 9"
