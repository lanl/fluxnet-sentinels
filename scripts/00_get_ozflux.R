# oz flux
# https://data.ozflux.org.au/portal/pub/viewColDetails.jspx?collection.id=602&collection.owner.id=107&viewType=anonymous
source("scripts/99_utils.R")
library(tidync)



parse_ozflux <- function(path_in) {
  # path_in <- "data/AliceSpringsMulga_L3_20110101_20111231.nc"
  test <- tidync(path_in) %>%
    activate("D2,D1,D0") %>%
    hyper_tibble() %>%
    janitor::clean_names()

  lookup <- c(h = "fh", p = "precip", le = "fe", netrad = "fn")
  test_new <- dplyr::select(test, any_of(c("month", "day", "year", "hour", "minute", "ta", "wd", "ws", "fc", "fh", "precip", "ps", "fe", "fn", "time", "C_ppm", "co2", "rh"))) %>%
    dplyr::rename(all_of(lookup)) %>%
    dplyr::mutate(across(where(is.numeric), ~ na_if(., -9999))) %>%
    dplyr::mutate(timestamp_start_fmt = (time * 60 * 60 * 24) + 4 + as.POSIXlt(strftime(as.Date("1800-01-01"), "%Y-%m-%d %H:%M"))) %>% # days since 1800 plus "4" tz offset
    dplyr::mutate(timestamp_end_fmt = timestamp_start_fmt + (30 * 60))

  # dplyr::mutate(hour = stringr::str_pad(hour, 2, pad = "0"),
  #     minute = stringr::str_pad(minute, 2, pad = "0"),
  #     month = stringr::str_pad(month, 2, pad = "0"),
  #     day = stringr::str_pad(day, 2, pad = "0")) %>%
  #   tidyr::unite("timestamp_end", all_of(c("year", "month", "day", "hour", "minute")), sep = "", remove = FALSE) %>%
  #   dplyr::mutate(timestamp_end_fmt = as.POSIXct(timestamp_end, format = "%Y%m%d%H%M")) %>%
  #   dplyr::mutate(timestamp_start_fmt = timestamp_end_fmt - (30 * 60)) %>%
  #   dplyr::mutate(timestamp_start = strftime(timestamp_start_fmt, "%Y%m%d%H%M"))

  test_new <- test_new %>%
    dplyr::mutate(timestamp_start = strftime(timestamp_start_fmt, "%Y%m%d%H%M"),
      timestamp_end = strftime(timestamp_end_fmt, "%Y%m%d%H%M")
    )
  #    %>%
  #   dplyr::select(-(ends_with("_fmt")))

  # skimr::skim(test_new)

  test_new
}

site_id <- "mulga"
flist <- list.files("data", pattern = "AliceSpringsMulga*", full.names = TRUE)

dt_subs <- lapply(flist, function(x) parse_ozflux(x))
dt <- dplyr::bind_rows(dt_subs)
# skimr::skim(dt)

outpath <- paste0("../../data/ozflux/", site_id, ".csv")
write.csv(dt, outpath, row.names = FALSE)
