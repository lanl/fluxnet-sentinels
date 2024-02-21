import sys
import pandas as pd

sys.path.append(".")
from src import utils

flist = ["data/grid_be-lon_7.csv", "data/grid_be-vie_7.csv", "data/grid_be-bra_7.csv"]
i = 0
dt = pd.read_csv(flist[i])
dt = dt[[x != "ppfd_in" for x in dt["indep"]]].reset_index(drop=True)
dt["site"] = utils.lower_to_mixed_case(flist[i].split("_")[1])
dt = dt[dt["r2"] > 0].sort_values("r2", ascending=False)
dt["fquant"] = dt["fquant"] * 100

utils.pdf_table(
    dt,
    "",
    "tables/grid_all.pdf",
    ["Dep", "Indep", "R2", "Effect", "Site"],
)
