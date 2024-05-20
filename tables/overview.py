import sys
import pandas as pd

sys.path.append(".")
from src import utils

base_case = {"wind_tolerance": 10, "n_days": 7, "event_quantile_effect": 0.9}

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

dt = dt[dt["wind_tolerance"] == base_case["wind_tolerance"]]
dt = dt[dt["n_days"] == base_case["n_days"]]
dt = dt[dt["event_quantile_effect"] == base_case["event_quantile_effect"]]

dt["dep"] = "co2"
dt["idep"] = "ta"
dt = dt.drop_duplicates("site", keep="last")

dt = dt[
    [
        "site",
        "event_r2",
        "event_effect",
        "event_wind",
        "n_days",
        "wind_tolerance",
        "event_quantile_effect",
    ]
]
dt["event_effect"] = round(dt["event_effect"], 2)
dt["event_wind"] = round(dt["event_wind"] * 100, 0)
dt["site"] = dt["site"] + r"\hspace{0.2em}"

# breakpoint()
# "-" in dt["site"].iloc[0]
# "-" in dt["site"]


utils.pdf_table(
    dt,
    "",
    "tables/overview.pdf",
    headers=[
        "Site",
        "$$R^2$$",
        "Effect",
        "Wind(t%)",
        "Days(n)",
        "Wind(tol)",
        "Effect(q)",
    ],
    # max_colwidths=[18, 8, 8, 8, 8, 8, 8],
)
