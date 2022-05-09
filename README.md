# `image_bench`

## How to use

- put `butteraugli_main` and/or `ssimulacra` somewhere in PATH
- place images to `./images`
- remove alpha chanel from the images  
  ```
  ./remove_alpha.sh ./images
  ```
- run benchmarks  
  ```
  ./gen.sh
  ```
- run `plot.ipynb` notebook
