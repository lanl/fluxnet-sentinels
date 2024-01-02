"""
    Given a site, event date, input/output data paths, variable pair, and bearing; Compute a sensitivity analysis to:
        event length, wind direction tolerance, and event averaging scheme
"""
import itertools
import subprocess
import pandas as pd

hyp = pd.read_csv("data/hyperparameters.csv")
grid = dict(tuple(hyp.groupby("parameter")))
grid_dict = {k: list(grid[k]["value"].values) for k in grid.keys()}

col_names = [k for k in grid_dict.keys()]
list_of_lists = [v for v in grid_dict.values()]
res = pd.DataFrame(list(itertools.product(*list_of_lists)))
res.columns = col_names

site = "BE-Lon"
date_event = "2008-08-23"

for i in range(res.shape[0]):
    # i = 0
    print(i)
    cmd = f"python scripts/01_fit_rolling.py --site {site} --date_event {date_event} --path_in ../../Data/Euroflux/BELon.csv --path_out figures/__rolling_fleurus_ --var_dep co2 --var_idep ta --bearing 235 --tolerance {int(res.iloc[i]['wind_tolerance'])} --n_days {int(res.iloc[i]['n_days'])} --event_quantile {res.iloc[i]['event_quantile']} --run_detailed --noplotting"
    subprocess.call(cmd, shell=True)

log = pd.read_csv("data/log.csv", header=None)
log_hyp = log.tail(hyp.shape[0])
log_hyp.to_csv("data/log_hyperparameter.csv", header=False, index=False)
