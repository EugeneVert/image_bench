#!/usr/bin/env python3

import argparse
from itertools import chain
from pathlib import Path

import pandas as pd

import metric


class Qualitiies():
    q64_99 = chain(
        range(64, 86, 2),
        range(86, 91, 1),
        [x/10 for x in range(905, 995, 5)])
    q2_32 = range(2, 34, 2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("format", type=str)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("cmd_arguments", type=str)
    parser.add_argument("-i", "--input_dir", type=Path, default="./images")
    parser.add_argument("--nproc", type=int, default=2)
    args = parser.parse_args()

    if args.format in ["cjxl", "cwebp"]:
        args.cmds = [f"{args.format}:-q {i} {args.cmd_arguments}"
                     for i in Qualitiies.q64_99]
    elif args.format in ["cavif"]:
        args.cmds = [f"{args.format}:-Q {i} {args.cmd_arguments}"
                     for i in Qualitiies.q64_99]
    elif args.format in ["avifenc"]:
        args.cmds = [f"{args.format}:-a cq-level={i} -a end-usage=q --min 0 --max 63 {args.cmd_arguments}"
                     for i in Qualitiies.q2_32]

    imageformats = (".png", ".jpg", ".webp")
    args.input = [f for f in args.input_dir.glob("*") if (f.is_file() and f.name.endswith(imageformats))]

    args_metrics = metric.ImageMetricsOption()
    if args_metrics.check_availability():
        args_metrics.do_metrics = True

    if not args.output_dir.exists():
        args.output_dir.mkdir()

    for image in args.input:
        args.csv_path = args.output_dir / (image.name + ".csv")
        metric.csv_write_header(args, args_metrics)
        metric.process_image(image, args, args_metrics)

    average_csv(args.output_dir)


def average_csv(dir_path: Path):
    dfs = []
    for i in dir_path.glob("*.csv"):
        print(i)
        f = open(i, 'r', newline='')
        reader = pd.read_csv(f, sep='\t')
        dfs.append(reader)
    average_tmp = pd.concat([*dfs]).groupby(level=0).mean()
    average = dfs[0]["Method"].to_frame().join(average_tmp)
    res = average.drop(columns=["Size", "px_count", "Res size"])

    with open(dir_path / "average.csv", "w", newline='') as f:
        f.write(res.to_csv(sep='\t', index=False))


if __name__ == "__main__":
    main()
