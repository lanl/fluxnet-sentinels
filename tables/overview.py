import sys
import pandas as pd

sys.path.append(".")
from src import utils

dt = pd.read_csv("data/log.csv")
dt.columns = [
    "date",
    "site",
    "wind_tolerance",
    "n_days",
    "event_quantile_effect",
    "false_positive_rate",
    "event_effect",
    "event_wind",
    "event_r2",
]

dt["dep"] = "co2"
dt["idep"] = "ta"
dt = dt.drop_duplicates("site", keep="last")

dt = dt[["site", "dep", "idep", "event_r2", "event_effect", "event_wind"]]
utils.pdf_table(
    dt,
    "test",
    "tables/overview.pdf",
    ["site", "dep", "idep", "event_r2", "event_effect", "event_wind"],
)
