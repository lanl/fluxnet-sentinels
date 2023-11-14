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

### Reference

```shell
## "effect size"
# p-value
# quantile of p-value relative to other windows
# abs(np.log(p-value))

# TODO: makes much more sense to have it be a coefficient value?
```

```shell
## dependent variables
# co2: carbon dioxide
# le: latent heat flux
# h: sensible heat flux
# fc: co2 flux

## independent variables
# ta: air temperature
# pa: atmospheric pressure
# ws: wind speed
# ppfd: photon flux density
# p: precipitation
# netrad: net solar radiation
# rh: relative humidity
```
