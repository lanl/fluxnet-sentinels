import sys
import glob
import janitor
import itertools
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sys.path.append(".")
from src import utils


def get_hour(x):
    if len(x) > 2:
        return x[0 : len(x) - 2]
    return "00"


def preprocess_dt(file_in):
    # file_in = "../../Data/Asiaflux/FxMt_FHK_2011_30m_02/FxMt_FHK_2011_30m_02.csv"
    # os.path.exists(file_in)

    names = pd.read_csv(file_in, nrows=1, encoding="Shift_JIS").clean_names()

    dt = pd.read_csv(
        file_in,
        skiprows=1,
        encoding="Shift_JIS",
        na_values=["-9999.0"],
    )
    dt.columns = [x for x in names.columns]
    dt = janitor.remove_empty(dt)
    dt = utils.amf_clean(dt)
    dt["i"] = [x for x in range(dt.shape[0])]

    # ---
    dt["hour"] = [get_hour(str(x)) for x in dt["time"]]
    dt["minute"] = [
        str(x)[len(str(x)) - 2 : len(str(x))] for x in [y for y in dt["time"]]
    ]
    dt["month"] = pd.to_datetime(
        [
            str(dt["year"].iloc[i]) + "-" + str(dt["doy"].iloc[i])
            for i in range(dt.shape[0])
        ],
        format="%Y-%j",
    ).strftime("%m")
    dt["day"] = pd.to_datetime(
        [
            str(dt["year"].iloc[i]) + "-" + str(dt["doy"].iloc[i])
            for i in range(dt.shape[0])
        ],
        format="%Y-%j",
    ).strftime("%d")
    dt["timestamp"] = pd.to_datetime(dt[["year", "month", "day", "hour", "minute"]])
    # ---

    if "rg_32" in dt.columns:
        dt = dt[dt["rg_32"] > 0]  # daytime

    return dt


# ---
site_id = "FHK"

f_list = glob.glob("../../Data/Asiaflux/*" + site_id + "*")
f_list = list(itertools.compress(f_list, [".csv" not in ff for ff in f_list]))
f_list = [glob.glob(ff + "/*.csv")[0] for ff in f_list]
dt_list = [preprocess_dt(ff) for ff in f_list]
dt = [
    dd[
        [
            "timestamp",
            "le",
            "h",
            "ws",
            "pa",
            "rh",
            "ppfd",
            "ta",
            "nee",
            "co",
            "year",
            "doy",
        ]
    ]
    for dd in dt_list
]
dt = pd.concat(dt).reset_index(drop=True)
dt["timestamp_start"] = dt["timestamp"]
dt["timestamp_end"] = dt["timestamp"]
dt = dt[dt["year"] < 2013]
dt.to_csv("../../Data/Asiaflux/" + site_id + ".csv", index=False)

# ---
g = sns.relplot(data=dt, x="doy", y="nee", row="year", hue="year", kind="line")
g.refline(x=70)
# plt.show()
plt.savefig("figures/__japanflux_nee.pdf")

g = sns.relplot(data=dt, x="doy", y="co", row="year", hue="year", kind="line")
g.refline(x=70)
# plt.show()
plt.savefig("figures/__japanflux_co.pdf")
