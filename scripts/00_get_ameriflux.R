source("scripts/99_utils.R")

check_site <- function(site_id) {
  # site_id <- "US-Uaf"
  print(site_id)

  fpaths <- list.files(path = "../../data/ameriflux/",
    pattern = "*.zip", full.names = TRUE)
  fpath <- fpaths[grep(site_id, fpaths)]
  dir.create("../../data/ameriflux", showWarnings = FALSE)
  if (length(grep(site_id, fpaths)) == 0) {
    fpath <- amf_download_base(
      user_id = "jstaaa",
      user_email = "jsta@lanl.gov",
      site_id = site_id,
      data_policy = "CCBY4.0",
      agree_policy = TRUE,
      intended_use = "other",
      intended_use_text = "testing download",
      out_dir = "../../data/ameriflux",
    )
  }

  base1 <- amf_clean(fpath)
  outpath <- paste0("../../data/ameriflux/", site_id, ".csv")
  write.csv(base1, outpath, row.names = FALSE)

  # library(ggplot2)
  # ggplot(data = base1) +
  # geom_point(aes(x = timestamp, y = co2, color = year))

  res <- base1 %>%
    dplyr::filter(year == 2011, month == 3) %>%
    dplyr::filter(!is.na(fc)) %>%
    nrow() > 0

  print(res)
  data.frame(covers_fukushima = res, path = outpath)
}

site <- amf_site_info()

# --- West Coast US
site_filtered <- site %>%
  clean_names() %>%
  dplyr::filter(data_start < 2011, data_end > 2012) %>%
  dplyr::filter(location_lat > 42, location_lat < 48.9,
    location_long < -116.9, location_long > -124.5) %>%
  dplyr::filter(data_policy == "CCBY4.0") %>%
  dplyr::filter(data_start < 2002)

head(site_filtered)
res <- lapply(site_filtered$site_id, check_site)

covers_fukushima <- as.logical(unlist(lapply(res, function(x) x[1])))
res_out <- site_filtered[covers_fukushima, ]
res_out$path <- as.character(unlist(lapply(res, function(x) x[2])))[covers_fukushima]

write.csv(res_out, "data/ameriflux_pnw.csv", row.names = FALSE)

# --- Australia
# dt <- get_sites(-33.867778, 151.21, "test")

# --- Brazil
test <- site[substring(site$SITE_ID, 0, 1) == "B", ]
test <- test[test$DATA_POLICY == "CCBY4.0", ]
# Brazil data doesn't span the required period :(
