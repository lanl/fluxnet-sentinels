library(ggmap)
suppressWarnings(suppressMessages(library(sf)))
suppressWarnings(suppressMessages(library(dplyr)))
suppressMessages(library(janitor))

coords_ire <- sf::st_as_sf(
  data.frame(lat = 50.45055, lon = 4.5350415),
  coords = c("lon", "lat"), crs = 4326)
sf::st_write(coords_ire, "data/fleurus.gpkg")
coords_ire$site_code <- "Fleurus"

dt_sites <- read.csv(
  system.file("extdata", "Site_metadata.csv", package = "FluxnetLSM")) %>%
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

gg <- qmplot(X, Y, data = m1_data,
  maptype = "toner-background", color = I("red")) +
  geom_text(data = m1_data, aes(label = site_code),
    vjust = 0,
    hjust = 0)

ggsave("figures/__map.pdf", gg)
