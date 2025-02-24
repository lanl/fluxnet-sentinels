## Eddy covariance towers as sentinels of abnormal radioactive material releases

[![Paper DOI](https://img.shields.io/badge/Paper-10.1007/s11356-025-36171-3-blue.svg)](https://doi.org/10.1007/s11356-025-36171-3) [![Code DOI](https://img.shields.io/badge/Code-10.5281/zenodo.13845254-blue.svg)](https://doi.org/10.5281/zenodo.13845254)

> Computing bivariate contrasts and time-series anomalies for event detection and flagging.

Code for the publication:

> Stachelek J., Vachel A. Kraklow, E. Christi Thompson, L. Turin Dickman, Emily Casleton, Sanna Sevanto, Ann Junghans. 2025. Eddy covariance towers as sentinels of abnormal radioactive material releases. 10.1007/s11356-025-36171-3

### Products

[manuscript/manuscript.pdf](manuscript/manuscript.pdf)

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

## Copyright notice

© 2024. Triad National Security, LLC. All rights reserved.
This program was produced under U.S. Government contract 89233218CNA000001 for Los Alamos
National Laboratory (LANL), which is operated by Triad National Security, LLC for the U.S.
Department of Energy/National Nuclear Security Administration. All rights in the program are
reserved by Triad National Security, LLC, and the U.S. Department of Energy/National Nuclear
Security Administration. The Government is granted for itself and others acting on its behalf a
nonexclusive, paid-up, irrevocable worldwide license in this material to reproduce, prepare
derivative works, distribute copies to the public, perform publicly and display publicly, and to permit
others to do so.
