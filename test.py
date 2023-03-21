# I think the climatology functions return an average over all the inputs not a time-series of footprints

import os
import janitor # clean_names
import numpy as np
import pandas as pd
import geopandas as gpd
import seaborn as sns
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from pyffp import calc_footprint_FFP_climatology as myfootprint

from pyffp import utils as ffputils
get_dd = ffputils.get_dd

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
dt["timestamp_start"] = pd.to_datetime(dt["timestamp_start"])
dt["timestamp_end"] = pd.to_datetime(dt["timestamp_end"])

# sns.histplot(data=dt, x="ustar")
# plt.show()

ustar = list(dt["ustar"].values[0:10])
umean = list(dt["ws"].values[0:10])
sigmav = list(dt["v_sigma"].values[0:10])
wind_dir = list(dt["wd"].values[0:10])

zm = [20.0 for i in range(10)]
h = [2000.0 for i in range(10)]
ol = [-100.0  for i in range(10)]

FFP = myfootprint.FFP_climatology(
    zm=zm,
    z0=0.01,
    # umean=umean,
    h=h,
    ol=ol,
    sigmav=sigmav,
    ustar=ustar,
    wind_dir=wind_dir
)

[k for k in FFP.keys()]
len(FFP["rs"])
len(FFP['fr'])
len(FFP['xr'][0])
len(FFP['yr'][0])

# ---

x_2d = FFP["x_2d"]
y_2d = FFP["y_2d"]
# set the origin at the BE-Lon station
origin_lon = 4.74613
origin_lat = 50.55159
x_2d_dd = np.vectorize(get_dd)(x_2d) + origin_lon
y_2d_dd = np.vectorize(get_dd)(y_2d) + origin_lat

# prepare contour inputs
clevs = FFP["fr"][::-1] # just reverses the order
clevs = [clev for clev in clevs if clev is not None]
levs = [clev for clev in clevs]
fs = FFP["fclim_2d"]
cs = [cm.jet(ix) for ix in np.linspace(0, 1, len(fs))]
f = fs[0]
c = cs[0]
cc = [c]*len(levs)

# generate GeoDataFrame of contours
fig, ax = plt.subplots(figsize=(10, 8))
cp = ax.contour(x_2d_dd, y_2d_dd, fs, levs, colors = cc, linewidths=0.5)
gdf = ffputils.contour_to_gdf(cp, "test.gpkg")
gdf["timestamp_start"] = list(dt["timestamp_start"].values[0:10])
# plt.show()
plt.close()

gpd.GeoDataFrame(geometry=gpd.points_from_xy(x=[origin_lon], y=[origin_lat])).to_file("BELon.gpkg", driver="GPKG")
gdf.to_file("test.gpkg", driver="GPKG")

