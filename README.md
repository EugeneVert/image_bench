# `image_bench`

## How to use

- compile `metric`  
  `cargo build --release`
- move `metric` to ./  
  `mv ./target/release/metric ./metric`
- put `butteraugli_main` and `ssimulacra` somewhere in PATH
- place the images to `./images`
- add alpha chanel to the images for ssimulacra to work (avifdec always decodes avif to png as srgba?)  
  ```
  ./add_alpha.sh ./images
  ```
- run benchmarks  
  ```
  ./gen.sh
  ```
- run `plot.ipynb` notebook
