library(dplyr)
library(janitor)
library(amerifluxr)

site <- amf_site_info()

site_filtered <- site %>%
  clean_names() %>%
  dplyr::filter(data_start < 2011, data_end > 2012) %>%
  dplyr::filter(location_lat > 58, location_long < -124) %>%
  dplyr::filter(data_policy == "CCBY4.0")

head(site_filtered)

check_site <- function(site_id) {
  # site_id = "US-Prr"
  print(site_id)

  fpaths <- list.files(path = "../../data/ameriflux/",
    pattern = "*.zip", full.names = TRUE)
  fpath <- fpaths[grep(site_id, fpaths)]
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

  base1 <- amf_read_base(
    file = fpath,
    unzip = TRUE,
    parse_timestamp = TRUE
  ) %>% clean_names()

    base1 <- setNames(base1, sub("_1_1_1", "", names(base1)))

  res <- base1 %>%
    dplyr::filter(year == 2011, month == 3) %>%
    dplyr::filter(!is.na(fc)) %>%
    nrow() > 0

  print(res)
  res
}

res <- lapply(site_filtered$site_id, check_site)
