#!/usr/bin/env python
import glob
import sys

import pandas as pd

arg = sys.argv[1]
input_path = "./"
if arg:
    input_path = arg + "/"
dfs = []
for i in glob.glob(input_path + "*.csv"):
    print(i)
    f = open(i, 'r', newline='')
    reader = pd.read_csv(f, sep='\t')
    dfs.append(reader)
average_tmp = pd.concat([*dfs]).groupby(level=0).mean()
average = dfs[0]["Method"].to_frame().join(average_tmp)
res = average.drop(columns=["Size", "px_count", "Res size"])

with open(input_path + "average.csv", "w", newline='') as f:
    f.write(res.to_csv(sep='\t', index=False))
