suppressWarnings(suppressMessages(library(sf)))
suppressWarnings(suppressMessages(library(dplyr)))
suppressMessages(library(janitor))
suppressMessages(library(mapview))
library(FluxnetLSM) # devtools::install_github("aukkola/FluxnetLSM")
library(leafem)
# library(openair)
# library(RFlux) # devtools::install_github("icos-etc/RFlux")
library(dplyr)
library(janitor)
library(amerifluxr)
library(progress)
library(ggmap) # devtools::install_github("stadiamaps/ggmap")
suppressMessages(library(cowplot))

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

get_gg_sub <- function(dt_sub, buffer_x = 0.02, buffer_y = 0.02) {
  bbox_sub <- c(left   = dt_sub$X - buffer_x,
    bottom = dt_sub$Y - buffer_y,
    right  = dt_sub$X + buffer_x,
    top    = dt_sub$Y + buffer_y)
  class(bbox_sub) <- "bbox"
  # ggmap::register_google()
  gg_map <- get_map(location = bbox_sub,
    maptype  = "stamen_toner_background",
    zoom     = 14)
  res <- ggmap(gg_map) +
    geom_point(aes(x = X, y = Y),
      data = dt_sub,
      colour = "red",
      fill = "red",
      alpha = .8) +
    geom_text(aes(x = X, y = Y, label = site_code), data = dt_sub,
      vjust = 0,
      hjust = 0)
  res
}
