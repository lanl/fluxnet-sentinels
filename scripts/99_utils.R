suppressWarnings(suppressMessages(library(sf)))
suppressWarnings(suppressMessages(library(dplyr)))
suppressMessages(library(janitor))
suppressMessages(library(mapview))
library(FluxnetLSM)
library(leafem)
# library(openair)
# library(RFlux) # devtools::install_github("icos-etc/RFlux")
library(dplyr)
library(janitor)
library(amerifluxr)
library(progress)
library(ggmap)

amf_clean <- function(fpath) {
  base_raw <- amf_read_base(
    file = fpath,
    unzip = TRUE,
    parse_timestamp = TRUE
  ) %>% clean_names()

  base1 <- setNames(base_raw,
    gsub("_\\d{1}_\\d{1}_\\d{1}", "", names(base_raw))) %>%
    dplyr::select(which(!duplicated(names(.)))) %>%
    remove_empty("cols")

  base1
}
