# `image_bench`

## How to use

- compile `metric`  
  `cargo build --release`
- move `metric` to ./  
  `mv ./target/release/metric ./metric`
- put `butteraugli_main` somewhere in PATH
- place images to `./images`
- run benchmarks  
  ```
  ./gen.sh
  ```
- run `plot.ipynb` notebook
