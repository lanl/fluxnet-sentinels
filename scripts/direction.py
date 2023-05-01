# https://gis.stackexchange.com/a/378750/32531
import pyproj
import janitor
import pandas as pd
import geopandas as gpd


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

geodesic = pyproj.Geod(
    ellps="WGS84"
)  # See: https://stackoverflow.com/questions/54873868/python-calculate-bearing-between-two-lat-long

df = gpd.read_file("dt_sites_close.gpkg")[["site_code", "geometry"]]
df = df[[x in ["BE-Lon", "BE-Bra"] for x in df["site_code"]]].reset_index(drop=True)

# Find azimuth of the two points by using their indexes
p1 = df.iloc[0]
p2 = df.iloc[1]
fwd_azimuth_goal, back_azimuth, distance = geodesic.inv(
    p1.geometry.x, p1.geometry.y, p2.geometry.x, p2.geometry.y
)
fwd_azimuth_goal