source("scripts/99_utils.R")

# oz flux
library(tidync)
# https://data.ozflux.org.au/portal/pub/viewColDetails.jspx?collection.id=602&collection.owner.id=107&viewType=anonymous
site_id <- "dargo"
test <- tidync("data/Dargo_2011_L3.nc") %>%
  activate("D0") %>%
  hyper_tibble() %>%
  janitor::clean_names()

lookup <- c(h = "fh", p = "precip", le = "fe", netrad = "fn")
test_new <- dplyr::select(test, all_of(c("month", "day", "year", "hour", "minute", "ta", "wd", "ws", "fc", "fh", "precip", "ps", "fe", "fn"))) %>%
  dplyr::rename(all_of(lookup)) %>%
  dplyr::mutate(across(where(is.numeric), ~ na_if(., -9999))) %>%
  dplyr::mutate(hour = stringr::str_pad(hour, 2, pad = "0"),
    minute = stringr::str_pad(minute, 2, pad = "0"),
    month = stringr::str_pad(month, 2, pad = "0"),
    day = stringr::str_pad(day, 2, pad = "0")) %>%
  tidyr::unite("timestamp_end", all_of(c("year", "month", "day", "hour", "minute")), sep = "", remove = FALSE) %>%
  dplyr::mutate(timestamp_end_fmt = as.POSIXct(timestamp_end, format = "%Y%m%d%H%M")) %>%
  dplyr::mutate(timestamp_start_fmt = timestamp_end_fmt - (30 * 60)) %>%
  dplyr::mutate(timestamp_start = strftime(timestamp_start_fmt, "%Y%m%d%H%M"))
#    %>%
#   dplyr::select(-(ends_with("_fmt")))

ggplot(test_new, aes(timestamp_end_fmt, ta)) + geom_point()
ggsave("test.pdf")

outpath <- paste0("../../data/ozflux/", site_id, ".csv")
write.csv(test_new, outpath, row.names = FALSE)
