## Fluxnet signatures

### Products

[figures/all.pdf](figures/all.pdf)

### Setup

```R
# rstats
remotes::update_packages(renv::dependencies("scripts/99_utils.R")$Package)
```

```shell
# python
mamba env create -f environment.yml
```

### Usage

```shell
make all
```
