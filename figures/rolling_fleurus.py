"""
    Analyze flux tower data associated with the Fleurus abnormal release. Should likely use scripts/01_fit_rolling.py instead.
```
python figures/rolling_fleurus.py --site_id BE-Lon
```
"""
import os
import sys
import janitor
import argparse
import itertools
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sys.path.append(".")
from src import rolling

parser = argparse.ArgumentParser()
parser.add_argument("--site_id", nargs=1, default="", type=str)
parser.add_argument("--window_size", nargs=1, default=["432"], type=int)
parser.add_argument("--bearing", nargs=1, default=["235"], type=int)
userargs = vars(parser.parse_args())
site = userargs["site_id"][0]
site_code = site.replace("-", "")
file_in = "../../Data/Euroflux/" + site_code + ".csv"
site_id = site_code.lower()

window_size = userargs["window_size"][0]
bearing = userargs["bearing"][0]

n_days = 7
dep_cols = ["co2", "fc", "le", "h", "co"]
indep_cols = ["ws", "p", "pa", "rh", "ppfd_in", "ta", "netrad"]
tolerance = 10
date_event = "2008-08-23"

# ---
dt, dt_select = rolling.preprocess_dt(file_in, dep_cols, indep_cols)
dt = janitor.remove_empty(dt)
dt_event = rolling.define_period(dt_select, n_days=n_days, date_event=date_event)
dt_event = janitor.remove_empty(dt_event)
indep_cols = list(
    itertools.compress(
        indep_cols, [col in list(dt_event.columns) for col in indep_cols]
    )
)


# ---
grid = rolling.make_grid(dt, dep_cols, indep_cols)
grid = rolling.regression_grid(
    grid, dt, dt_event, site_id, n_days, window_size=window_size
)

varpair = ("co2", "ta")
varpair_code = "v".join(varpair) + "_"

path_pdist = "data/pdist_" + varpair_code + site_code + ".csv"
path_pevent = "data/p_event_" + varpair_code + site_code + ".csv"
path_event_index = "data/event_index_" + varpair_code + site_code + ".csv"
if (not os.path.exists(path_pdist)) or (not os.path.exists(path_pevent)):
    _, pdist, timestamps, event_index, p_event = rolling.p_quantile(
        dt, dt_event, varpair[0], varpair[1], window_size=window_size
    )
    pd.DataFrame({"timestamp": timestamps, "pdist": pdist}).to_csv(
        path_pdist, index=False
    )
    pd.DataFrame({"pevent": p_event}, index=[0]).to_csv(path_pevent, index=False)
    pd.DataFrame({"event_index": event_index}, index=[0]).to_csv(
        path_event_index, index=False
    )
pdist = pd.read_csv(path_pdist)
timestamps = [x for x in pdist["timestamp"]]
p_event = float(
    pd.read_csv(
        path_pevent,
    ).values[0]
)
event_index = float(
    pd.read_csv(
        path_event_index,
    ).values[0]
)

g = sns.histplot(abs(np.log(pdist["pdist"])))
g.axvline(abs(np.log(p_event)))
# plt.show()
plt.savefig("figures/__" + varpair_code + site_code + "_hist.pdf")

# ---
wind_fraction = rolling.towards(dt, bearing, tolerance)
pd.DataFrame({"wind_fraction": wind_fraction}).to_csv(
    "data/wind_fraction.csv", index=False
)

g_data = pd.DataFrame(
    {
        "timestamp": timestamps,
        "index": [x for x in range(len(pdist))],
        "p": abs(np.log([x for x in pdist["pdist"]])),
        "wind_fraction": wind_fraction,
    }
)

g_data["timestamp"] = pd.to_datetime(g_data["timestamp"])

tt = [
    (g_data.iloc[i]["wind_fraction"] >= g_data.iloc[int(event_index)]["wind_fraction"])
    and (g_data.iloc[i]["p"] >= g_data.iloc[int(event_index)]["p"])
    for i in range(g_data.shape[0])
]

plt.close()
fig, ax1 = plt.subplots(figsize=(9, 6))
g = sns.lineplot(data=g_data, x="timestamp", y="p", ax=ax1)
g.axvline(pd.to_datetime(date_event), color="yellow")
g.axhline(abs(np.log(p_event)), color="darkgreen")
g.set_ylim(0, np.nanquantile(g_data["p"], [1]) + 10)
ax1.set_ylabel("effect size (blue line, green line [event])")
ax1.text(pd.to_datetime(date_event), 3, "<-\nAbnormal\nEvent", color="red")

ax2 = ax1.twinx()
g2 = sns.lineplot(data=g_data, x="timestamp", y="wind_fraction", ax=ax2, color="black")
g2.set_ylim(-1, 1)
[
    g2.axvline(g_data[tt].iloc[i]["timestamp"], color="orange")
    for i in range(g_data[tt].shape[0])
]
# g_data[
#     (g_data["p"] > abs(np.log(p_event))).values and (g_data["test"] > 0.7).values
# ].shape
ax2.set_ylabel("fraction wind towards (black line)")
plt.suptitle(
    site
    + "("
    + ",".join(varpair)
    + ")"
    + r"$\alpha$"
    + "="
    + str(round(sum(tt) / g_data.shape[0], 2))
)
ax1.set_xlabel("")
ax2.set_xlabel("")
# plt.show()
plt.savefig("figures/__rolling_fleurus_" + site_id + ".pdf")
