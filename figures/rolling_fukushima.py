import sys
import janitor
import tabulate
import subprocess
import pandas as pd

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
subprocess.call(
    "pdfcrop.pl figures/__rolling_grid_"
    + site_id
    + ".pdf figures/__rolling_grid_"
    + site_id
    + ".pdf",
    shell=True,
)
