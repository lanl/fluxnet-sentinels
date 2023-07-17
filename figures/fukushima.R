source("scripts/99_utils.R")

sites <- read.csv("data/ameriflux_pnw.csv")

# ---
coords <- sf::st_as_sf(
  sites,
  coords = c("location_long", "location_lat"), crs = 4326)

# mapview(coords)

us <- c(left = -171.63, bottom = 51.93, right = -138.85, top = 70.7)
gg <- get_stamenmap(us, zoom = 5, maptype = "toner-lite") %>%
  ggmap() +
  geom_point(aes(x = location_long, y = location_lat), data = sites, alpha = .5, color = "red") +
  geom_text(aes(x = location_long, y = location_lat, label = site_id), data = sites)

ggsave("figures/__map_fukushima.pdf", gg)

# ---

# dt <- amf_clean(sites$path[1])
