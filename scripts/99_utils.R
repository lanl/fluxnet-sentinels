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

  new_names <- gsub("_\\d{1}_\\d{1}_\\d{1}", "", names(base_raw))
  new_names <- gsub("_\\d{1}", "", new_names)
  new_names <- gsub("\\.\\d{1}", "", new_names)
  base1 <- setNames(base_raw, new_names)

  n_na <- unlist(lapply(seq_len(ncol(base1)), function(i) sum(is.na(base1[, i]))))
  base1 <- base1[, order(n_na)]
  new_names <- gsub("\\.\\d{1}", "", names(base1))
  base1 <- setNames(base1, new_names)

  base1 <- base1 %>%
    dplyr::select(which(!duplicated(names(.)))) %>%
    remove_empty("cols")

  base1
}
