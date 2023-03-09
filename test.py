import os
import janitor # clean_names
import pandas as pd
import seaborn as sns
from pyffp import calc_footprint_FFP as myfootprint

if os.path.exists("../scripts"):
    shim = "../"
else:
    shim = ""

# dt <- read.csv(
#     paste0(shim, "../../Data/Euroflux/BE-Lon/L2-L4_2004-2012/EFDC_L2_Flx_BELon_2008_v017_30m.txt"),
#     header = TRUE,
#     colClasses = c("TIMESTAMP_START" = "character", "TIMESTAMP_END" = "character"),
#     na.strings = "-9999") %>%
#     clean_names()

dt = pd.read_csv(
    shim
    + "../../Data/Euroflux/BE-Lon/L2-L4_2004-2012/EFDC_L2_Flx_BELon_2008_v017_30m.txt",
    na_values=["-9999"],
    dtype = {"TIMESTAMP_START":str, "TIMESTAMP_END":str}
).clean_names()
dt = dt[dt["ustar"] >= 0.1].reset_index(drop=True)

# sns.histplot(data=dt, x="ustar")
# plt.show()

ustar = dt["ustar"].values[0]
umean = dt["ws"].values[0]
sigmav = dt["v_sigma"].values[0]
wind_dir = dt["wd"].values[0]

FFP = myfootprint.FFP(
    zm=20.0,
    umean=umean,
    h=2000.0,
    ol=-100.0,
    sigmav=sigmav,
    ustar=ustar,
    wind_dir=wind_dir,
    rs=[20.0, 40.0, 60.0, 80.0],
)
