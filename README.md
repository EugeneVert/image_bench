# `image_bench`

## How to use

- compile `metric`  
  `cargo build --release`
- symlink `metric` to ./  
  `ln -s ./target/release/metric ./metric`
- place images in ./
- run benchmarks
  `./bench_ims avif.sh`
  `./bench_ims jxl.sh`
- get average results
  `cd avif; ../average_csv_pd.py; cd ../cjxl; ../average_csv_pd.py; cd ..`
- run `plot.ipynb` notebook
