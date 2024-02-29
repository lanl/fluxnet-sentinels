"""This script is deprecated in favor of 01_fit_rolling and rolling.py"""

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

# ---
site = "be-vie"
file_in = "../../Data/Euroflux/BE-Vie/EFDC_L2_Flx_BEVie_2008_v010_30m.txt"

dt, dt_select = rolling.preprocess_dt(file_in, dep_cols, indep_cols)
dt = janitor.remove_empty(dt)
grid = rolling.make_grid(dt, dep_cols, indep_cols)

ax = sns.heatmap(grid.pivot("dep", "indep", values="r2"), annot=True)
ax.set(xlabel="", ylabel="")
ax.xaxis.tick_top()
plt.suptitle(site + ": Regression R2")
# plt.show()
plt.savefig("figures/__rolling_heatmap_" + site + ".pdf")
plt.close()

dt_event = rolling.define_period(dt_select, n_days=n_days)
rolling.grid_define_pquant(
    grid, dt, dt_event, "data/grid_" + site + "_" + str(n_days) + ".csv"
)
grid = pd.read_csv("data/grid_" + site + "_" + str(n_days) + ".csv")
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
    "echo ## " + site + "| cat - mdtable.md > temp && mv temp mdtable.md",
    shell=True,
)
subprocess.call(
    "echo \\pagenumbering{gobble}| cat - mdtable.md > temp && mv temp mdtable.md",
    shell=True,
)
subprocess.call(
    "pandoc mdtable.md -V fontsize=14pt -o figures/__rolling_grid_" + site + ".pdf"
)
subprocess.call(
    "pdfcrop figures/__rolling_grid_"
    + site
    + ".pdf figures/__rolling_grid_"
    + site
    + ".pdf"
)

# ---
site = "be-bra"
file_in = "../../Data/Euroflux/BE-Bra/EFDC_L2_Flx_BEBra_2008_v016_30m.txt"

dt, dt_select = rolling.preprocess_dt(file_in, dep_cols, indep_cols)
grid = rolling.make_grid(dt, dep_cols, indep_cols)

ax = sns.heatmap(grid.pivot("dep", "indep", values="r2"), annot=True)
ax.set(xlabel="", ylabel="")
ax.xaxis.tick_top()
plt.suptitle(site + ": Regression R2")
plt.savefig("figures/__rolling_heatmap_" + site + ".pdf")
plt.close()

dt_event = rolling.define_period(dt_select, n_days=n_days)
rolling.grid_define_pquant(
    grid, dt, dt_event, "data/grid_" + site + "_" + str(n_days) + ".csv"
)
grid = pd.read_csv("data/grid_" + site + "_" + str(n_days) + ".csv")
test = grid[grid["r2"] > 0.05].reset_index(drop=True)

mdtable = tabulate.tabulate(
    test,
    headers=["Explanatory", "Regressor", "R2", r"Event Percentile"],
    tablefmt="simple",
    showindex=False,
)
with open("mdtable.md", "w") as f:
    f.write(mdtable)

subprocess.call(
    "echo ## " + site + "| cat - mdtable.md > temp && mv temp mdtable.md",
    shell=True,
)
subprocess.call(
    "echo \\pagenumbering{gobble}| cat - mdtable.md > temp && mv temp mdtable.md",
    shell=True,
)
subprocess.call(
    "pandoc mdtable.md -V fontsize=14pt -o figures/__rolling_grid_" + site + ".pdf"
)
subprocess.call(
    "pdfcrop figures/__rolling_grid_"
    + site
    + ".pdf figures/__rolling_grid_"
    + site
    + ".pdf"
)

# ---
site = "be-lon"
file_in = (
    "../../Data/Euroflux/BE-Lon/L2-L4_2004-2012/EFDC_L2_Flx_BELon_2008_v017_30m.txt"
)

dt, dt_select = rolling.preprocess_dt(file_in, dep_cols, indep_cols)
grid = rolling.make_grid(dt, dep_cols, indep_cols)

ax = sns.heatmap(grid.pivot("dep", "indep", values="r2"), annot=True)
ax.set(xlabel="", ylabel="")
ax.xaxis.tick_top()
plt.suptitle(site + ": Regression R2")
plt.savefig("figures/__rolling_heatmap_" + site + ".pdf")
plt.close()

dt_event = rolling.define_period(dt_select, n_days=n_days)
rolling.grid_define_pquant(
    grid, dt, dt_event, "data/grid_" + site + "_" + str(n_days) + ".csv"
)
grid = pd.read_csv("data/grid_" + site + "_" + str(n_days) + ".csv")
test = grid[grid["r2"] > 0.05].reset_index(drop=True)

mdtable = tabulate.tabulate(
    test,
    headers=["Explanatory", "Regressor", "R2", r"Event Percentile"],
    tablefmt="simple",
    showindex=False,
)
with open("mdtable.md", "w") as f:
    f.write(mdtable)

subprocess.call(
    "echo ## " + site + "| cat - mdtable.md > temp && mv temp mdtable.md",
    shell=True,
)
subprocess.call(
    "echo \\pagenumbering{gobble}| cat - mdtable.md > temp && mv temp mdtable.md",
    shell=True,
)
subprocess.call(
    "pandoc mdtable.md -V fontsize=14pt -o figures/__rolling_grid_" + site + ".pdf"
)
subprocess.call(
    "pdfcrop figures/__rolling_grid_"
    + site
    + ".pdf figures/__rolling_grid_"
    + site
    + ".pdf"
)

# ---

# try plotting a timeseries and distribution of quantiles
_, pdist, event_index, p_event = rolling.p_quantile(dt, dt_event, "co2", "ta")
g = sns.histplot(abs(np.log(pdist)))
g.axvline(abs(np.log(p_event)))
# plt.show()
plt.savefig("figures/__co2vta_belon_hist.pdf")

g = sns.lineplot(
    data=pd.DataFrame(
        {"index": [x for x in range(len(pdist))], "p": abs(np.log(pdist))}
    ),
    x="index",
    y="p",
)
g.axvline(event_index, color="yellow")
g.axhline(abs(np.log(p_event)), color="darkgreen")
# plt.show()
plt.ylim(0, 150)
plt.savefig("figures/__co2vta_belon_line.pdf")

# ---

# dep = grid["dep"][0]
# indep = grid["indep"][0]

sns.lmplot(x="ta", y="co2", hue="period", data=dt_event, scatter_kws={"s": 1})
# plt.yscale("log")
# plt.show()
# min(dt_event["ppfd_in"])
plt.close()
