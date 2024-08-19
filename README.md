## Eddy covariance towers as sentinels of abnormal radioactive material releases

[![Paper DOI](https://img.shields.io/badge/Paper-DOI-blue.svg)](https://doi.org) [![Code DOI](https://img.shields.io/badge/Code-DOI-blue.svg)](https://doi.org) [![Data DOI](https://img.shields.io/badge/Data-DOI-blue.svg)](https://doi.org)

Code for the publication:

> Stachelek J., Vachel A. Kraklow, E. Christi Thompson, L. Turin Dickman, Emily Casleton, Sanna Sevanto, Ann Junghans. _In-prep_. Eddy covariance towers as sentinels of abnormal radioactive material releases.

### Products

[manuscript/manuscript.pdf](manuscript/manuscript.pdf)

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
mamba activate fluxnet
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
