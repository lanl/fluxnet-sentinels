library(ggmap) # install_github("stadiamaps/ggmap")
source("scripts/99_utils.R")

coords_ire <- sf::st_as_sf(
  data.frame(lat = 50.45055, lon = 4.5350415),
  coords = c("lon", "lat"), crs = 4326
)
coords_ire$site_code <- "Fleurus"
if (!file.exists("data/fleurus.gpkg")) {
  sf::st_write(coords_ire, "data/fleurus.gpkg", append = FALSE)
}

dt_sites <- read.csv(
  system.file("extdata", "Site_metadata.csv", package = "FluxnetLSM")
) %>%
  clean_names() %>%
  # dplyr::mutate_all(na_if, "") %>%
  st_as_sf(coords = c("site_longitude", "site_latitude"), crs = 4326)

dt_sites$dist <- unlist(list(unlist(st_distance(coords_ire, dt_sites)))) / 1609.34
dt_sites_close <- dt_sites[dt_sites$dist < 100, ] %>%
  dplyr::arrange(dist)
sf::st_write(dt_sites_close, "dt_sites_close.gpkg", append = FALSE)

# head(dplyr::select(dt_sites_close, site_code, dist))
# st_coordinates(dt_sites_close[1,])

m1_data <- dplyr::bind_rows(dt_sites_close, coords_ire)
m1_data <- cbind(m1_data, st_coordinates(m1_data))
m1_data <- sf::st_drop_geometry(dplyr::select(m1_data, X, Y, site_code))
m1_data <- dplyr::filter(
  m1_data,
  site_code %in% c("BE-Lon", "BE-Vie", "BE-Bra", "Fleurus")
)

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
gg_euro_overview <- ggmap(gg_map) +
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
# gg_euro_overview

dt_sub <- dplyr::filter(m1_data, site_code == "BE-Lon")
gg_euro_belon <- get_gg_sub(dt_sub)

dt_sub <- dplyr::filter(m1_data, site_code == "BE-Vie")
gg_euro_bevie <- get_gg_sub(dt_sub, label_color = "white")

dt_sub <- dplyr::filter(m1_data, site_code == "BE-Bra")
gg_euro_bebra <- get_gg_sub(dt_sub, label_color = "white")

gg <- cowplot::plot_grid(gg_euro_overview, gg_euro_bebra, gg_euro_belon, gg_euro_bevie)
ggsave("figures/__map.pdf", gg)
