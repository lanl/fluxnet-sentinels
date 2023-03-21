import janitor # for .clean_names
import pandas as pd
import seaborn as sns

dt = pd.read_csv(
    "../../Data/Euroflux/BE-Lon/L2-L4_2004-2012/EFDC_L2_Flx_BELon_2008_v017_30m.txt"
).clean_names()

# --- define before, during, and after periods
# 10 days before and after
# Before: Aug 12, 13, 14, 15, 16, 17, 18, 19, 20, 21
# During: Aug 22, 23, 24
# After: Aug 25, 26, 27, 28, 29, 30, 31, 1,2,3
dt["timestamp_start"] = pd.to_datetime(dt["timestamp_start"], format="%Y%m%d%H%M")
dt["timestamp_end"] = pd.to_datetime(dt["timestamp_end"], format="%Y%m%d%H%M")
dt["period"] = None
dt.loc[
    (dt["timestamp_end"] < pd.to_datetime("2008-08-22"))
    & (dt["timestamp_start"] > pd.to_datetime("2008-08-11")),
    "period",
] = "before"
dt.loc[
    (dt["timestamp_end"] < pd.to_datetime("2008-08-25"))
    & (dt["timestamp_start"] > pd.to_datetime("2008-08-21")),
    "period",
] = "during"
dt.loc[dt["timestamp_start"] > pd.to_datetime("2008-08-24"),
    "period",
] = "after"

dt[["timestamp_start", "timestamp_end", "period"]].tail(20)
