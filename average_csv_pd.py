#!/usr/bin/env python
import glob
import pandas as pd


dfs = []
for i in glob.glob("./*.csv"):
    f = open(i, 'r', newline='')
    reader = pd.read_csv(f, sep='\t')
    dfs.append(reader)
average_tmp = pd.concat([*dfs]).groupby(level=0).mean()
average = dfs[0]["Method"].to_frame().join(average_tmp)
res = average.drop(columns=["Size", "px_count", "Res size"])

with open("./average.csv", "w", newline='') as f:
    f.write(res.to_csv(sep='\t', index=False))