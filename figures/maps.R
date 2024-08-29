options(debug = TRUE)
library(ggmap) # install_github("stadiamaps/ggmap")
library(ggspatial)
source("scripts/99_utils.R")

generate_overview <- function(sites, site_codes, buffer_x = 0.5, buffer_y = 0.2,
    nudge_x = 0.3, nudge_y = -0.1, label_color = "black") {
  # site_codes <- c("BE-Lon", "BE-Vie", "BE-Bra", "IRE")
  # label_colors = c("black", "white", "white")

  m1_data <- dplyr::filter(sites, site_code %in% site_codes)
  m1_data <- dplyr::mutate(m1_data, dist = dist * 1.60934)  # mi to km
  m1_data <- sf::st_drop_geometry(
    dplyr::select(m1_data, X, Y, site_code, dist))

  print(m1_data)
  print(buffer_x)
  bbox <- c(left   = min(m1_data$X) - buffer_x,
    bottom = min(m1_data$Y) - buffer_y,
    right  = max(m1_data$X) + buffer_x,
    top    = max(m1_data$Y) + buffer_y)
  class(bbox) <- "bbox"

  gg_map <- get_map(location = bbox,
    maptype  = "stamen_toner_background")

  # https://stackoverflow.com/a/20580465
  bb <- attr(gg_map, "bb")
  sbar <- data.frame(lon.start = c(bb$ll.lon + 0.1 * (bb$ur.lon - bb$ll.lon)),
    lon.end = c(bb$ll.lon + 0.25 * (bb$ur.lon - bb$ll.lon)),
    lat.start = c(bb$ll.lat + 0.1 * (bb$ur.lat - bb$ll.lat)),
    lat.end = c(bb$ll.lat + 0.1 * (bb$ur.lat - bb$ll.lat)))
  sbar$distance <- dist_haversine(long = c(sbar$lon.start, sbar$lon.end),
    lat = c(sbar$lat.start, sbar$lat.end))
  ptspermm <- 2.83464567  # need this because geom_text uses mm, and themes use pts. Urgh.

  gg_overview <- ggmap(gg_map) +
    geom_point(
      data = m1_data, aes(x = X, y = Y),
      color = I("red")
    ) +
    geom_text(
      data = m1_data, aes(x = X, y = Y, label = site_code),
      vjust = nudge_y,
      hjust = nudge_x,
      size = 6,
      color = label_color
    ) +
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
  list(gg_overview = gg_overview, m1_data = m1_data)
}

# --- ire
sites <- get_sites(50.45055, 4.5350415, "IRE")
overview <- generate_overview(sites, c("BE-Lon", "BE-Vie", "BE-Bra", "IRE"))
gg_overview <- overview$gg_overview
# ggsave("test.pdf", gg_overview)
m1_data <- overview$m1_data

dt_sub <- dplyr::filter(m1_data, site_code == "BE-Lon")
gg_euro_belon <- get_gg_sub(dt_sub)
dt_sub <- dplyr::filter(m1_data, site_code == "BE-Vie")
gg_euro_bevie <- get_gg_sub(dt_sub, label_color = "white")
dt_sub <- dplyr::filter(m1_data, site_code == "BE-Bra")
gg_euro_bebra <- get_gg_sub(dt_sub, label_color = "white")

gg <- cowplot::plot_grid(gg_overview, gg_euro_bebra, gg_euro_belon, gg_euro_bevie) +
  cowplot::panel_border(color = "black", size = 1.5)
ggsave("figures/__map_fleurus.pdf", gg)

# --- jp-fhk
sites <- get_sites(37.423056, 141.033056, "Fukushima", 190)
overview <- generate_overview(sites, c("JP-FHK", "Fukushima"),
  nudge_x = 0.6, label_color = "red", buffer_x = 0.7)
gg_overview <- overview$gg_overview
m1_data <- overview$m1_data

dt_sub <- dplyr::filter(m1_data, site_code == "JP-FHK")
gg_jp_fhk <- get_gg_sub(dt_sub, label_color = "white")

gg <- cowplot::plot_grid(gg_overview, gg_jp_fhk)
ggsave("figures/__map_fhk.pdf", gg)

# --- us-wrc
sites <- get_sites(45.8205, -121.9519, "US-Wrc", 190)
overview <- generate_overview(sites, c("US-Wrc"), buffer_x = 3, buffer_y = 2.5)
gg_overview <- overview$gg_overview
m1_data <- overview$m1_data

dt_sub <- dplyr::filter(m1_data, site_code == "US-Wrc" & !is.na(dist))
gg_us_wrc <- get_gg_sub(dt_sub, label_color = "white")

gg <- cowplot::plot_grid(gg_overview, gg_us_wrc)
ggsave("figures/__map_wrc.pdf", gg)

# -- us-gle
sites <- get_sites(41.3665, -106.2399, "US-Gle", 190)
overview <- generate_overview(sites, c("US-Gle"), buffer_x = 3, buffer_y = 2.5)
gg_overview <- overview$gg_overview
m1_data <- overview$m1_data

dt_sub <- dplyr::filter(m1_data, site_code == "US-Gle" & is.na(dist))
gg_us_gle <- get_gg_sub(dt_sub, label_color = "white")

gg <- cowplot::plot_grid(gg_overview, gg_us_gle)
ggsave("figures/__map_gle.pdf", gg)

# -- oz-mul
sites <- get_sites(-22.2828, 133.2493, "OZ-Mul", 190)
overview <- generate_overview(sites, c("OZ-Mul"), buffer_x = 3, buffer_y = 2.5)
gg_overview <- overview$gg_overview
m1_data <- overview$m1_data

dt_sub <- dplyr::filter(m1_data, site_code == "OZ-Mul" & is.na(dist))
gg_oz_mul <- get_gg_sub(dt_sub, label_color = "white")

gg <- cowplot::plot_grid(gg_overview, gg_oz_mul)
ggsave("figures/__map_mul.pdf", gg)

# --- fukushima
# https://r-spatial.org/r/2018/10/25/ggplot2-sf.html
crsrobin <- paste0("+proj=robin +lon_0=-180 +x_0=0 +y_0=0 +ellps=WGS84",
  " +datum=WGS84 +units=m +no_defs")

dt_fuku_df <- data.frame(
  site_code = c("Fukushima", "US-Wrc", "US-Gle", "OZ-Mul"),
  lat = c(37.423056, 45.8205, 41.3665, -22.2828),
  lon = c(141.033056, -121.9519, -106.2399, 133.2493))
dt_fuku <- st_transform(
  st_as_sf(dt_fuku_df, coords = c("lon", "lat"), crs = 4326), crs = crsrobin)
dt_fuku_df <- cbind(dt_fuku_df, st_coordinates(dt_fuku))

library(rnaturalearth)
world <- ne_countries(scale = "medium", returnclass = "sf")
xmin <- -4320952
xmax <- 6376465
ymin <- -2383193 * 1.12
ymax <- 4891261 * 1.12
arrow_y <- ((xmin + xmax) / 2) + abs(ymin - ymax) * 0.32
arrow_x_end <- ((xmin + xmax) / 2) + abs(xmin - xmax) * 0.16
gg_overview <- ggplot(
  data = st_transform(st_break_antimeridian(world, lon_0 = 180), crs = crsrobin)) +
  geom_sf() +
  geom_sf(data = dt_fuku, color = "red") +
  geom_text(data = dt_fuku_df, aes(x = X, y = Y * 1.06, label = site_code),
    check_overlap = FALSE) +
  coord_sf(
    xlim = c(xmin * 1.2, xmax  * 1.1),
    ylim = c(ymin * 1.3, ymax * 1.3), expand = TRUE) +
  annotate("text", x = (2 + arrow_x_end) / 2, y = arrow_y - abs(ymin - ymax) * 0.1,
    label = "Plume direction", size = 5) +
  geom_segment(lineend = "butt", linejoin = "mitre", linewidth = 1.5,
    arrow = arrow(length = unit(0.2, "inches")),
    aes(x = 2, y = arrow_y,
      xend = arrow_x_end, yend = arrow_y)) +
  theme_minimal() +
  xlab("lon") + ylab("lat") +
  theme(
    # axis.title = element_blank(),
    axis.ticks = element_line(color = "black"))
ggsave("test.pdf", gg_overview)

gg <- cowplot::plot_grid(gg_overview, gg_us_wrc, gg_oz_mul, gg_us_gle) +
  cowplot::panel_border(color = "black", size = 1.5)
ggsave("figures/__map_fukushima.pdf", gg)
