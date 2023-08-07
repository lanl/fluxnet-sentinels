"""
    Preprocessing Euroflux data files
"""
import sys
import glob
import pandas as pd

sys.path.append(".")
from src.rolling import preprocess_dt

site_id = "BELon"
dep_cols = ["co2", "fc", "le", "h", "co"]
indep_cols = ["ws", "p", "pa", "rh", "ppfd_in", "ta", "netrad"]

f_list = glob.glob("../../Data/Euroflux/BE-Lon/L2-L4_2004-2012/*" + site_id + "*.txt")

dt_list = [
    preprocess_dt(f_list[i], dep_cols, indep_cols)[0] for i in range(len(f_list))
]
dt = pd.concat(dt_list).reset_index(drop=True)
dt.to_csv("../../Data/Euroflux/" + site_id + ".csv", index=False)
