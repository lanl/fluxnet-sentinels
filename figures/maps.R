library(ggmap) # install_github("stadiamaps/ggmap")
source("scripts/99_utils.R")

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

generate_overview <- function(sites, site_codes) {
  # site_codes <- c("BE-Lon", "BE-Vie", "BE-Bra", "IRE")
  # label_colors = c("black", "white", "white")

  m1_data <- dplyr::filter(sites, site_code %in% site_codes)
  m1_data <- dplyr::mutate(m1_data, dist = dist * 1.60934)  # mi to km
  m1_data <- sf::st_drop_geometry(
    dplyr::select(m1_data, X, Y, site_code, dist))

  print(m1_data)
  buffer_x <- 0.5
  buffer_y <- 0.2
  bbox <- c(left   = min(m1_data$X) - buffer_x,
    bottom = min(m1_data$Y) - buffer_y,
    right  = max(m1_data$X) + buffer_x,
    top    = max(m1_data$Y) + buffer_y)
  class(bbox) <- "bbox"

  gg_map <- get_map(location = bbox,
    maptype  = "stamen_toner_background")
  gg_overview <- ggmap(gg_map) +
    geom_point(
      data = m1_data, aes(x = X, y = Y),
      color = I("red")
    ) +
    geom_text(
      data = m1_data, aes(x = X, y = Y, label = site_code),
      vjust = -0.1,
      hjust = 0.3,
      size = 6
    )
  list(gg_overview = gg_overview, m1_data = m1_data)
}

# --- ire
sites <- get_sites(50.45055, 4.5350415, "fleurus")
overview <- generate_overview(sites, c("BE-Lon", "BE-Vie", "BE-Bra", "IRE"))
gg_overview <- overview$gg_overview
m1_data <- overview$m1_data

dt_sub <- dplyr::filter(m1_data, site_code == "BE-Lon")
gg_euro_belon <- get_gg_sub(dt_sub)
dt_sub <- dplyr::filter(m1_data, site_code == "BE-Vie")
gg_euro_bevie <- get_gg_sub(dt_sub, label_color = "white")
dt_sub <- dplyr::filter(m1_data, site_code == "BE-Bra")
gg_euro_bebra <- get_gg_sub(dt_sub, label_color = "white")

gg <- cowplot::plot_grid(gg_overview, gg_euro_bebra, gg_euro_belon, gg_euro_bevie)
ggsave("figures/__map.pdf", gg)

# --- fukushima
sites <- get_sites(37.423056, 141.033056, "fukushima", 190)
overview <- generate_overview(sites, c("JP-FHK", "fukushima"))
gg_overview <- overview$gg_overview
m1_data <- overview$m1_data

dt_sub <- dplyr::filter(m1_data, site_code == "JP-FHK")
gg_jp_fhk <- get_gg_sub(dt_sub, label_color = "white")

gg <- cowplot::plot_grid(gg_overview, gg_jp_fhk)
ggsave("figures/test.pdf", gg)
