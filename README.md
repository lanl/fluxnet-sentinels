## Fluxnet signatures

### Products

`/figures/all.pdf`

### Setup

```R
remotes::update_packages(renv::dependencies("scripts/99_utils.R")$Package)
```

```shell
mamba env create -f environment.yml
```

### Usage

```shell
make all
```
