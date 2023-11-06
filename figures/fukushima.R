source("scripts/99_utils.R")

sites <- read.csv("data/ameriflux_pnw.csv")

# ---
coords <- sf::st_as_sf(
  sites,
  coords = c("location_long", "location_lat"), crs = 4326)

# mapview(coords)

us <- c(left = -126.89, bottom = 41.24, right = -115.83, top = 50.6)
gg <- get_map(location = us,
  maptype  = "stamen_toner_background") %>%
  ggmap() +
  geom_point(aes(x = location_long, y = location_lat),
    data = sites, alpha = .5, color = "red") +
  geom_text(aes(x = location_long, y = location_lat, label = site_id), data = sites)

gg_pnw_wrc <- get_gg_sub(
  dplyr::rename(sites, c("Y" = "location_lat",
    "X" = "location_long",
    "site_code" = "site_id"))
)

gg2 <- cowplot::plot_grid(gg, gg_pnw_wrc)

ggsave("figures/__map_fukushima.pdf", gg2)

# ---

# dt <- amf_clean(sites$path[1])
