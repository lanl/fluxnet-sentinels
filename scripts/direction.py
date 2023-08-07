"""
    https://gis.stackexchange.com/a/378750/32531
"""
import sys
import janitor
import pandas as pd
import seaborn as sns
import geopandas as gpd
import matplotlib.pyplot as plt

sys.path.append(".")
from src import rolling


def preprocess_dt(file_in, dep_cols, indep_cols):
    dt = pd.read_csv(
        file_in,
        na_values=["-9999.0"],
    ).clean_names()
    dt = janitor.remove_empty(dt)
    dt["timestamp_start"] = pd.to_datetime(dt["timestamp_start"], format="%Y%m%d%H%M")
    dt["timestamp_end"] = pd.to_datetime(dt["timestamp_end"], format="%Y%m%d%H%M")
    dt["hour"] = [int(x.strftime("%H")) for x in dt["timestamp_start"]]

    # breakpoint()
    # ax = sns.lineplot(data=dt, x="timestamp_start", y="netrad")
    # ax.set_xlim(pd.to_datetime("2008-01-01"), pd.to_datetime("2008-03-01"))
    # plt.show()

    if "ppfd_in" in dt.columns:
        dt = dt[dt["ppfd_in"] > 100]  # daytime
    else:
        indep_cols = [x for x in indep_cols if x != "ppfd_in"]
        dt = dt[dt["netrad"] > 0]  # daytime

    dt = janitor.remove_empty(dt)
    dep_cols = [x for x in dep_cols if x in dt.columns]

    # dt[dep_cols].head()
    # dt[indep_cols].describe()
    dt[dep_cols[1]] = dt[dep_cols[1]] + abs(min(dt[dep_cols[1]])) + 0.01
    dt[dep_cols[2]] = dt[dep_cols[2]] + abs(min(dt[dep_cols[2]])) + 0.01
    dt[dep_cols[3]] = dt[dep_cols[3]] + abs(min(dt[dep_cols[3]])) + 0.01

    dt_select = dt[["timestamp_start", "timestamp_end"] + dep_cols + indep_cols]
    return (dt, dt_select)


# ---

dep_cols = ["co2", "fc", "le", "h"]
indep_cols = ["ws", "p", "pa", "rh", "ppfd_in", "ta", "netrad"]
site = "be-lon"
file_in = (
    "../../Data/Euroflux/BE-Lon/L2-L4_2004-2012/EFDC_L2_Flx_BELon_2008_v017_30m.txt"
)

dt, dt_select = preprocess_dt(file_in, dep_cols, indep_cols)

# Find azimuth of the two points by using their indexes
df = gpd.read_file("dt_sites_close.gpkg")[["site_code", "geometry"]]
df = df[[x in ["BE-Lon", "BE-Bra"] for x in df["site_code"]]].reset_index(drop=True)
fwd_azimuth_goal = rolling.bearing(df.iloc[0], df.iloc[1])

plt.close()
ax = df.plot("site_code")
for i in range(df["site_code"].shape[0]):
    coords = df.iloc[i].geometry.coords
    ax.text(float(coords.xy[0][0]), float(coords.xy[1][0]), s=df.iloc[i]["site_code"])
plt.show()

plt.close()
g = sns.histplot(data=dt, x="wd")
g.axvline(fwd_azimuth_goal)
plt.show()


# given:
#   2 gdf points
#

# return
