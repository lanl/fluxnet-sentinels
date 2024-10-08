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

get_gg_sub <- function(dt_sub, buffer_x = 0.02, buffer_y = 0.02, label_color = "black",
    vjust = 0, hjust = 0) {
  bbox_sub <- c(left   = dt_sub$X - buffer_x,
    bottom = dt_sub$Y - buffer_y,
    right  = dt_sub$X + buffer_x,
    top    = dt_sub$Y + buffer_y)
  class(bbox_sub) <- "bbox"

  gg_map <- get_googlemap(center = c(lon = dt_sub$X, lat = dt_sub$Y),
    maptype  = "satellite",
    zoom     = 16)

  # https://stackoverflow.com/a/20580465
  bb <- attr(gg_map, "bb")
  sbar <- data.frame(lon.start = c(bb$ll.lon + 0.1 * (bb$ur.lon - bb$ll.lon)),
    lon.end = c(bb$ll.lon + 0.25 * (bb$ur.lon - bb$ll.lon)),
    lat.start = c(bb$ll.lat + 0.1 * (bb$ur.lat - bb$ll.lat)),
    lat.end = c(bb$ll.lat + 0.1 * (bb$ur.lat - bb$ll.lat)))
  sbar$distance <- dist_haversine(long = c(sbar$lon.start, sbar$lon.end),
    lat = c(sbar$lat.start, sbar$lat.end))
  ptspermm <- 2.83464567  # need this because geom_text uses mm, and themes use pts. Urgh.

  res <- ggmap(gg_map) +
    geom_point(aes(x = X, y = Y),
      data = dt_sub,
      colour = "red",
      fill = "red",
      alpha = .8) +
    geom_text(aes(x = X, y = Y, label = site_code), data = dt_sub,
      vjust = vjust,
      hjust = hjust,
      size = 6,
      color = label_color) +
    geom_segment(data = sbar,
      aes(x = lon.start,
        xend = lon.end,
        y = lat.start,
        yend = lat.end),
      arrow = arrow(angle = 90, length = unit(0.1, "cm"),
        ends = "both", type = "open"),
      color = label_color) +
    geom_text(data = sbar,
      aes(x = (lon.start + lon.end) / 2,
        y = lat.start + 0.025 * (bb$ur.lat - bb$ll.lat),
        label = paste(format(distance,
          digits = 4,
          nsmall = 2),
        "km")),
      hjust = 0.5,
      vjust = 0,
      size = 8 / ptspermm,
      color = label_color)
  res
}

get_sites <- function(lat, lon, site_tag, distance_threshold = 100) {
  coords <- sf::st_as_sf(
    data.frame(lat = lat, lon = lon),
    coords = c("lon", "lat"), crs = 4326
  )
  coords$site_code <- site_tag

  out_file <- paste0("data/", site_tag, ".gpkg")
  if (!file.exists(out_file)) {
    sf::st_write(coords, out_file, append = FALSE)
  }

  dt_sites <- read.csv(
    system.file("extdata", "Site_metadata.csv", package = "FluxnetLSM")
  ) %>%
    clean_names() %>%
    # dplyr::mutate_all(na_if, "") %>%
    st_as_sf(coords = c("site_longitude", "site_latitude"), crs = 4326)

  dt_sites$dist <- unlist(list(unlist(
    st_distance(coords, dt_sites)))) / 1609.34 # m to miles
  dt_sites_close <- dt_sites[dt_sites$dist < distance_threshold, ] %>%
    dplyr::arrange(dist)
  sf::st_write(dt_sites_close,
    paste0("dt_sites_close", site_tag, ".gpkg"), append = FALSE)

  # head(dplyr::select(dt_sites_close, site_code, dist))
  # st_coordinates(dt_sites_close[1,])

  m1_data <- dplyr::bind_rows(dt_sites_close, coords)
  m1_data <- cbind(m1_data, st_coordinates(m1_data))
  m1_data
}

dist_haversine <- function(long, lat) {

  long <- long * pi / 180
  lat <- lat * pi / 180
  dlong <- (long[2] - long[1])
  dlat  <- (lat[2] - lat[1])

  # Haversine formula:
  R <- 6371
  a <- sin(dlat / 2) * sin(dlat / 2) + cos(lat[1]) * cos(lat[2]) * sin(dlong / 2) * sin(dlong / 2)
  c <- 2 * atan2(sqrt(a), sqrt(1 - a))
  d <- R * c
  return(d) # in km
}
