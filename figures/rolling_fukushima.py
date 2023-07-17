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
dep_cols = ["co2", "fc", "le", "h"]
indep_cols = ["ws", "p", "pa", "rh", "ppfd_in", "ta", "netrad"]

date_event = "2011-03-11"

# ---
site = "US-Wrc"
file_in = "../../Data/Ameriflux/" + site + ".csv"
site_id = "us-wrc"

dt, dt_select = rolling.preprocess_dt(file_in, dep_cols, indep_cols)
dt = janitor.remove_empty(dt)
dt_event = rolling.define_period(dt_select, n_days=n_days, date_event=date_event)

# ---
grid = rolling.make_grid(dt, dep_cols, indep_cols)
rolling.regression_grid(grid, dt, dt_event, site_id, n_days)

# ---
test2 = rolling.towards(dt, 285, 80)
pd.DataFrame({"test": test2}).to_csv("data/test.csv", index=False)

path_pdist = "data/pdist_levrh_uswrc.csv"
path_pevent = "data/p_event_levrh_uswrc.csv"
path_event_index = "data/event_index_levrh_uswrc.csv"
if (not os.path.exists(path_pdist)) or (not os.path.exists(path_pevent)):
    _, pdist, event_index, p_event = rolling.p_quantile(dt, dt_event, "le", "rh")
    pd.DataFrame({"pdist": pdist}).to_csv(path_pdist, index=False)
    pd.DataFrame({"pevent": p_event}, index=[0]).to_csv(path_pevent, index=False)
    pd.DataFrame({"event_index": event_index}, index=[0]).to_csv(
        path_event_index, index=False
    )
pdist = [float(x) for x in pd.read_csv(path_pdist).values]
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

g = sns.histplot(abs(np.log(pdist)))
g.axvline(abs(np.log(p_event)))
# plt.show()
plt.savefig("figures/__levrh_uswrc_hist.pdf")

g_data = pd.DataFrame(
    {"index": [x for x in range(len(pdist))], "p": abs(np.log(pdist)), "test": test2}
)
tt = [
    (g_data.iloc[i]["test"] > 0.637) and (g_data.iloc[i]["p"] >= 24.6)
    for i in range(g_data.shape[0])
]

plt.close()
fig, ax1 = plt.subplots(figsize=(9, 6))
g = sns.lineplot(data=g_data, x="index", y="p", ax=ax1)
g.axvline(event_index, color="yellow")
g.axhline(abs(np.log(p_event)), color="darkgreen")
g.set_ylim(0, 180)
ax1.set_ylabel("effect size (blue line, green line [event])")
ax1.text(event_index, 3, "<-\nFukushima\nDisaster", color="red")

ax2 = ax1.twinx()
g2 = sns.lineplot(data=g_data, x="index", y="test", ax=ax2, color="black")
g2.set_ylim(-1, 1)
# g_data.iloc[int(event_index)]["p"]
[
    g2.axvline(g_data[tt].iloc[i]["index"], color="orange")
    for i in range(g_data[tt].shape[0])
]
# g_data[
#     (g_data["p"] > abs(np.log(p_event))).values and (g_data["test"] > 0.7).values
# ].shape
ax2.set_ylabel("fraction wind towards (black line)")
plt.suptitle("US-Wrc")
# plt.show()
plt.savefig("figures/__rolling_fukushima.pdf")
