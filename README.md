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
# interaction term F-value
# quantile of F-value relative to other windows

# raw comparison in the initial variable pair screening step:
# stats.percentileofscore(fdist_compilation, f_fl, nan_policy="omit") / 100

# in the event detection flagging step:
# np.quantile(<fdist during event>, [event_quantile_effect]) -> event_effect
# other events flagged if f >= event_effect
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
