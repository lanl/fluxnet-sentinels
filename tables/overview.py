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

dt = dt[["site", "event_r2", "event_effect", "event_wind"]]
dt["event_effect"] = round(dt["event_effect"], 2)
dt["event_wind"] = round(dt["event_wind"] * 100, 0)

utils.pdf_table(
    dt,
    "",
    "tables/overview.pdf",
    ["Site", "R2", "Effect", "Wind %"],
)
