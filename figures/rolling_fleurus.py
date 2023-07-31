import os
import sys
import janitor
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sys.path.append(".")
from src import rolling


n_days = 7
dep_cols = ["co2", "fc", "le", "h", "co"]
indep_cols = ["ws", "p", "pa", "rh", "ppfd_in", "ta", "netrad"]
tolerance = 40
date_event = "2008-08-23"

# ---
site = "BE-Lon"
file_in = (
    r"../../Data/Euroflux/BE-Lon/L2-L4_2004-2012/EFDC_L2_Flx_BELon_2008_v017_30m.txt"
)
site_id = site.lower()
site_code = site_id.replace("-", "")

dt, dt_select = rolling.preprocess_dt(file_in, dep_cols, indep_cols)
dt = janitor.remove_empty(dt)
dt_event = rolling.define_period(dt_select, n_days=n_days, date_event=date_event)

# ---
grid = rolling.make_grid(dt, dep_cols, indep_cols)
grid = rolling.regression_grid(grid, dt, dt_event, site_id, n_days)

varpair = ("co2", "ta")
varpair_code = "v".join(varpair) + "_"

path_pdist = "data/pdist_" + varpair_code + site_code + ".csv"
path_pevent = "data/p_event_" + varpair_code + site_code + ".csv"
path_event_index = "data/event_index_" + varpair_code + site_code + ".csv"
if (not os.path.exists(path_pdist)) or (not os.path.exists(path_pevent)):
    _, pdist, timestamps, event_index, p_event = rolling.p_quantile(
        dt, dt_event, varpair[0], varpair[1]
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