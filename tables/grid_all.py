import sys
import itertools
import pandas as pd

sys.path.append(".")
from src import utils


def process_grid(i):
    # i = 0
    dt = pd.read_csv(flist[i])
    dt = dt[[x != "ppfd_in" for x in dt["indep"]]].reset_index(drop=True)
    dt["site"] = utils.lower_to_mixed_case(flist[i].split("_")[1])
    dt = dt[dt["r2"] > 0].sort_values("r2", ascending=False)
    dt["fquant"] = dt["fquant"] * 100

    dt_names = [x for x in dt.columns]
    if "n_days" in dt_names:
        dt = dt[list(itertools.compress(dt_names, [x != "n_days" for x in dt_names]))]

    dt = dt.values.tolist()
    # dt = dt + [SEPARATING_LINE]
    return dt


# NOTE
# values here are different than the overview table because here they're relative to the POR
# in the overview table they're limited to only during the event

# # IRE case study
flist = ["data/grid_be-lon_7.csv", "data/grid_be-vie_7.csv", "data/grid_be-bra_7.csv"]
grid_list = [process_grid(i) for i in range(len(flist))]

utils.pdf_table(
    list(itertools.chain(*grid_list)),
    "",
    "tables/grid_all.pdf",
    ["Dep", "Indep", "R2", "Effect", "Site"],
    render_only=False,
)

# # Fukushima case study

flist = ["data/grid_oz-mul_7.csv", "data/grid_us-gle_7.csv", "data/grid_us-wrc_7.csv"]
grid_list = [process_grid(i) for i in range(len(flist))]

utils.pdf_table(
    list(itertools.chain(*grid_list)),
    "",
    "tables/grid_all_fukushima.pdf",
    ["Dep", "Indep", "R2", "Effect", "Site"],
    render_only=False,
)
