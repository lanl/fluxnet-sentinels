"""
    Preprocessing Euroflux data files from:
    http://www.europe-fluxdata.eu/home/data/request-data
```
python scripts/00_get_euroflux.py --site_id BE-Bra
python scripts/00_get_euroflux.py --site_id BE-Lon --subfolder L2-L4_2004-2012
```
"""
import sys
import glob
import argparse
import pandas as pd

sys.path.append(".")
from src.rolling import preprocess_dt

parser = argparse.ArgumentParser()
parser.add_argument("--site_id", nargs=1, default="", type=str)
parser.add_argument("--subfolder", nargs=1, default="", type=str)
userargs = vars(parser.parse_args())
site = userargs["site_id"][0]
subfolder = userargs["subfolder"]
site_code = site.replace("-", "")

dep_cols = ["co2", "fc", "le", "h", "co"]
indep_cols = ["ws", "p", "pa", "rh", "ppfd_in", "ta", "netrad"]

if len(subfolder) < 1:
    f_list_target = "../../Data/Euroflux/" + site + "/*" + site_code + "*.txt"
else:
    f_list_target = (
        "../../Data/Euroflux/" + site + "/" + subfolder[0] + "/*" + site_code + "*.txt"
    )
f_list = glob.glob(f_list_target)

dt_list = [
    preprocess_dt(f_list[i], dep_cols, indep_cols)[0] for i in range(len(f_list))
]

dt = pd.concat(dt_list).reset_index(drop=True)
dt.to_csv("../../Data/Euroflux/" + site_code + ".csv", index=False)
