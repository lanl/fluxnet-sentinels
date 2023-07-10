import os
import sys
import janitor
import tabulate
import subprocess
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
grid = rolling.make_grid(dt, dep_cols, indep_cols)

dt_event = rolling.define_period(dt_select, n_days=n_days, date_event=date_event)

test = rolling.towards(dt, 285, 80)
pd.DataFrame({"test": test}).to_csv("data/test.csv", index=False)

# ---
rolling.grid_define_pquant(
    grid, dt, dt_event, "data/grid_" + site_id + "_" + str(n_days) + ".csv"
)

# ---

grid = pd.read_csv("data/grid_" + site_id + "_" + str(n_days) + ".csv")
test = grid[grid["r2"] > 0.05].reset_index(drop=True)
test = test[[x != "ppfd_in" for x in test["indep"]]].reset_index(drop=True)


mdtable = tabulate.tabulate(
    test,
    headers=["Explanatory", "Regressor", "R2", r"Event Percentile"],
    tablefmt="simple",
    showindex=False,
)
with open("mdtable.md", "w") as f:
    f.write(mdtable)

subprocess.call(
    "echo ## " + site_id + "| cat - mdtable.md > temp && mv temp mdtable.md",
    shell=True,
)
subprocess.call(
    "echo \\pagenumbering{gobble}| cat - mdtable.md > temp && mv temp mdtable.md",
    shell=True,
)
subprocess.call(
    "pandoc mdtable.md -V fontsize=14pt -o figures/__rolling_grid_" + site_id + ".pdf",
    shell=True,
)
try:  # conda pdfcrop
    subprocess.check_call(
        "pdfcrop.pl figures/__rolling_grid_"
        + site_id
        + ".pdf figures/__rolling_grid_"
        + site_id
        + ".pdf",
        shell=True,
    )
except:  # system pdfcrop
    subprocess.call(
        "pdfcrop figures/__rolling_grid_"
        + site_id
        + ".pdf figures/__rolling_grid_"
        + site_id
        + ".pdf",
        shell=True,
    )

# ---
rolling.towards(dt, dt_event, 285, 160)


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

g = sns.lineplot(
    data=pd.DataFrame(
        {"index": [x for x in range(len(pdist))], "p": abs(np.log(pdist))}
    ),
    x="index",
    y="p",
)
g.axvline(event_index, color="yellow")
g.axhline(abs(np.log(p_event)), color="darkgreen")

plt.ylim(0, 150)
# plt.show()
plt.savefig("figures/__levrh_uswrc_line.pdf")
