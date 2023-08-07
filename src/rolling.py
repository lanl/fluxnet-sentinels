"""
    Utility functions for driving rolling analyses
"""
import os
import pyproj
import janitor
import tabulate
import itertools
import subprocess
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from datetime import timedelta
import statsmodels.formula.api as smf
from numpy_ext import rolling_apply as rolling_apply_ext


def p_interact(x, y, timestamp):
    dt_sub = pd.DataFrame({"x": x, "y": y})
    dt_sub["period"] = (
        ["before" for _ in range(247)]
        + ["during" for _ in range(70)]
        + ["after" for _ in range(249)]
    )

    date = timestamp.reset_index(drop=True)[int(np.floor(len(timestamp) / 2))]

    if (not any(pd.notna(dt_sub.y.values))) or (not any(pd.notna(dt_sub.x.values))):
        return np.nan, date

    if (sum(pd.notna(dt_sub.y.values)) < 7) or (sum(pd.notna(dt_sub.x.values)) < 7):
        return np.nan, date

    try:
        model = smf.ols("np.log(y) ~ x * period", data=dt_sub).fit()
        res = sm.stats.anova_lm(model, typ=1)
        res = res.to_dict()["PR(>F)"]["x:period"]
        return res, date
    except:  # SVD did not converge. or too much missing data?
        return np.nan, date


def p_quantile(dt, dt_event, dep, indep):
    # p_quantile(dt, dt_event, "co2", "ta") # ~ 0.14
    # p_quantile(dt, dt_event, "fc", "ws")
    # dep = "fc"
    # indep = "ws"
    print((dep, indep))
    model = smf.ols("np.log(" + dep + ") ~ " + indep + " * period", data=dt_event).fit()
    p_fl = sm.stats.anova_lm(model, typ=1).to_dict()["PR(>F)"][indep + ":period"]

    # dt_event["period"].value_counts()

    window_size = 566  # 30 min * (3 + 7 + 7) days?

    if ("timestamp_start" in [x for x in dt.columns]) and (
        "timestamp" not in [x for x in dt.columns]
    ):
        dt["timestamp"] = dt["timestamp_start"]

    # i = 1
    # dt.iloc[[566 * i]]["timestamp_start"]
    # dt.iloc[[566 + (566 * i)]]["timestamp_start"]
    # dt["timestamp_start"].tail()
    # p_interact(dt[indep].values[0:window_size], dt[dep].values[0:window_size])

    # breakpoint()
    # any(pd.notna(dt[indep].values))
    # any(pd.notna(dt[dep].values))
    # p_interact(dt[indep].values[0:566], dt[dep].values[0:566])
    # p_interact(dt[indep].values[566:1132], dt[dep].values[566:1132])
    # any(pd.notna(dt[dep].values[566:1132]))
    # any(pd.notna(dt[indep].values[566:1132]))

    pdist = rolling_apply_ext(
        p_interact,
        window_size,
        dt[indep].values,
        dt[dep].values,
        dt["timestamp"],
        n_jobs=1,
    )

    pdist_compilation = [float(x[0]) for x in pdist]
    timestamps = [x[1] for x in pdist]

    # _, pdist, event_index, p_event
    return (
        stats.percentileofscore(pdist_compilation, p_fl, nan_policy="omit") / 100,
        pdist_compilation,
        timestamps,
        dt_event.index[0],
        p_fl,
    )


def preprocess_dt(file_in, dep_cols, indep_cols, daylight_threshold=100):
    dt = pd.read_csv(
        file_in,
        na_values=["-9999.0"],
    ).clean_names()
    dt = janitor.remove_empty(dt)

    try:  # ameriflux format
        dt["timestamp_start"] = pd.to_datetime(
            dt["timestamp_start"], format="%Y%m%d%H%M"
        )
        dt["timestamp_end"] = pd.to_datetime(dt["timestamp_end"], format="%Y%m%d%H%M")
    except:  # japanflux format
        dt["timestamp_start"] = pd.to_datetime(
            dt["timestamp_start"], format="%Y-%m-%d %H:%M:%S"
        )
        dt["timestamp_end"] = pd.to_datetime(
            dt["timestamp_end"], format="%Y-%m-%d %H:%M:%S"
        )
    dt["hour"] = [int(x.strftime("%H")) for x in dt["timestamp_start"]]

    # breakpoint()
    # ax = sns.lineplot(data=dt, x="timestamp_start", y="netrad")
    # ax.set_xlim(pd.to_datetime("2008-01-01"), pd.to_datetime("2008-03-01"))
    # plt.show()

    # calculate which hours have low ppfd, exclude those hours
    if "ppfd_in" in dt.columns:
        test = dt[["hour", "ppfd_in"]].groupby("hour", as_index=False).mean()
        daylight_hours = test[test["ppfd_in"] > daylight_threshold][
            "hour"
        ].values.tolist()
        dt = dt[[x in daylight_hours for x in dt["hour"]]]
    elif "netrad" in dt.columns:
        indep_cols = [x for x in indep_cols if x != "ppfd_in"]
        dt = dt[dt["netrad"] > 0]  # daytime
    else:
        indep_cols = [x for x in indep_cols if x != "ppfd_in"]
        test = dt[["hour", "ppfd"]].groupby("hour", as_index=False).mean()
        daylight_hours = test[test["ppfd"] > daylight_threshold]["hour"].values.tolist()
        dt = dt[[x in daylight_hours for x in dt["hour"]]]

    dt = janitor.remove_empty(dt)
    dep_cols = [x for x in dep_cols if x in dt.columns]
    indep_cols = [x for x in indep_cols if x in dt.columns]

    dt = dt[[x for x in ~dt[dep_cols + indep_cols].isna().all(axis=1)]]

    # dt[dep_cols].head()
    # dt[indep_cols].describe()
    # breakpoint()
    # sum(pd.isna(dt["co2"])) / dt.shape[0]
    for i, _ in enumerate(dep_cols):
        # i = 0
        dt[dep_cols[i]] = dt[dep_cols[i]] + abs(dt[dep_cols[i]].min()) + 0.01

    dt_select = dt[["timestamp_start", "timestamp_end"] + dep_cols + indep_cols]
    return (dt, dt_select)


def make_grid(dt, dep_cols, indep_cols):
    if not "ppfd_in" in dt.columns:
        indep_cols = [x for x in indep_cols if x != "ppfd_in"]
    dep_cols = [x for x in dep_cols if x in dt.columns]
    indep_cols = [x for x in indep_cols if x in dt.columns]

    grid = pd.DataFrame(
        list(itertools.product(dep_cols, indep_cols)), columns=["dep", "indep"]
    )

    res = []
    for i in range(grid.shape[0]):
        # print(i)
        res.append(
            round(
                abs(
                    smf.ols(
                        grid.iloc[[i]]["dep"].values[0]
                        + " ~ "
                        + grid.iloc[[i]]["indep"].values[0],
                        data=dt,
                    )
                    .fit()
                    .rsquared_adj
                ),
                2,
            )
        )

    grid["r2"] = res

    return grid


def define_period(dt_select, date_event="2008-08-23", n_days=10):
    # 10 days before and after

    dt_select = dt_select.copy()
    dt_select["period"] = None

    dt_select.loc[
        (dt_select["timestamp_end"] < pd.to_datetime(date_event) - timedelta(days=1))
        & (
            dt_select["timestamp_start"]
            > pd.to_datetime(date_event) - timedelta(days=n_days + 2)
        ),
        "period",
    ] = "before"
    dt_select.loc[
        (dt_select["timestamp_end"] < pd.to_datetime(date_event) + timedelta(days=2))
        & (
            dt_select["timestamp_start"]
            > pd.to_datetime(date_event) - timedelta(days=2)
        ),
        "period",
    ] = "during"
    dt_select.loc[
        (dt_select["timestamp_start"] > pd.to_datetime(date_event) + timedelta(days=1))
        & (
            dt_select["timestamp_start"]
            < pd.to_datetime(date_event) + timedelta(days=n_days + 2)
        ),
        "period",
    ] = "after"
    dt_event = dt_select[[x is not None for x in dt_select["period"]]].copy()
    return dt_event


def grid_define_pquant(grid, dt, dt_event, out_path="data/grid.csv", overwrite=False):
    if not os.path.exists(out_path) or overwrite:
        print("Making: " + out_path)
        pquant = []
        for i in range(grid.shape[0]):
            # i = 0
            pquant_i = p_quantile(
                dt,
                dt_event,
                grid.iloc[[i]]["dep"].values[0],
                grid.iloc[[i]]["indep"].values[0],
            )
            pquant.append(
                round(
                    abs(pquant_i[0]),
                    2,
                )
            )
        # TODO: why is the process being killed before this line when running with multiprocessing?

        grid["pquant"] = pquant
        grid = grid.sort_values("pquant")
        grid.to_csv(out_path, index=False)
        return grid


def bearing(p1, p2):
    geodesic = pyproj.Geod(
        ellps="WGS84"
    )  # See: https://stackoverflow.com/questions/54873868/python-calculate-bearing-between-two-lat-long

    fwd_azimuth_goal, _, _ = geodesic.inv(
        p1.geometry.x, p1.geometry.y, p2.geometry.x, p2.geometry.y
    )
    if fwd_azimuth_goal < 0:
        fwd_azimuth_goal = fwd_azimuth_goal + 365

    return fwd_azimuth_goal


def within_bearing(wd, within_bearing_args={"bearing": 20, "tolerance": 10}):
    """
    within_bearing([10, 30, 45, 115, 280], {"bearing":45, "tolerance":40}) # 0.6
    within_bearing([10, 30, 45, 115, 280], {"bearing":45, "tolerance":50}) # 0.6

    within_bearing([10, 30, 45, 115, 280], {"bearing":315, "tolerance":40}) # 0.2
    within_bearing([10, 30, 45, 115, 280], {"bearing":315, "tolerance":55}) # 0.4
    """
    bearing = within_bearing_args["bearing"]
    tolerance = within_bearing_args["tolerance"]
    lower = bearing - tolerance
    upper = bearing + tolerance

    if upper > 365:
        upper = abs(365 - upper)

    if lower < 0:
        lower = lower + 365

    def _compute(x, upper, lower):
        """
        _compute(10, upper = 95, lower = 360) # True
        _compute(10, upper = 85, lower = 5) # True
        _compute(10, upper = 5, lower = 260) # False
        _compute(2, upper = 5, lower = 260) # True
        _compute(350, upper = 5, lower = 260) # True
        """
        if pd.isna(x):
            return False

        if lower < upper:
            return (x <= upper) and (x >= lower)
        else:
            return (x <= upper) or (x >= lower)

    is_within = [_compute(x, upper, lower) for x in wd]
    res = round(sum(is_within) / len(is_within), 3)

    return res


def towards(dt, bearing, tolerance, uses_letters=False):
    # identify time points where wd falls within "towards" tolerance

    if uses_letters:
        dt = dt.rename(columns={"wd": "direction"})
        compass_key = pd.DataFrame(
            {
                "direction": [
                    "CLM",
                    "N",
                    "NW",
                    "NNE",
                    "WSW",
                    "SW",
                    "WNW",
                    "NNW",
                    "W",
                    "NE",
                    "ESE",
                    "E",
                    "ENE",
                    "S",
                    "SSW",
                    "SSE",
                    "SE",
                ],
                "wd": [
                    pd.NA,
                    0,
                    315,
                    22.5,
                    247.5,
                    225,
                    292.5,
                    337.5,
                    270,
                    45,
                    112.5,
                    90,
                    67.5,
                    180,
                    202.5,
                    157.5,
                    135,
                ],
            }
        )
        dt = dt.merge(compass_key, how="left")

    within_bearing_args = {"bearing": bearing, "tolerance": tolerance}

    window_size = 566  # 30 min * (3 + 7 + 7) days?

    is_towards = rolling_apply_ext(
        within_bearing,
        window_size,
        dt["wd"].values,
        n_jobs=1,
        within_bearing_args=within_bearing_args,
    )
    # is_towards = is_towards[~np.isnan(is_towards)]

    return is_towards


def regression_grid(grid, dt, dt_event, site_id, n_days, overwrite=False):
    grid_define_pquant(
        grid,
        dt,
        dt_event,
        "data/grid_" + site_id + "_" + str(n_days) + ".csv",
        overwrite,
    )

    grid = pd.read_csv("data/grid_" + site_id + "_" + str(n_days) + ".csv")
    res = grid[grid["r2"] > 0.05].reset_index(drop=True)
    res = res[[x != "ppfd_in" for x in res["indep"]]].reset_index(drop=True)

    mdtable = tabulate.tabulate(
        res,
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
        "pandoc mdtable.md -V fontsize=14pt -o figures/__rolling_grid_"
        + site_id
        + ".pdf",
        shell=True,
    )
    try:  # conda pdfcrop
        subprocess.check_call(
            "pdfcrop.pl figures/__rolling_grid_"
            + site_id
            + ".pdf figures/__rolling_grid_"
            + site_id
            + ".pdf",
            shell=True,
        )
    except:  # system pdfcrop
        subprocess.call(
            "pdfcrop figures/__rolling_grid_"
            + site_id
            + ".pdf figures/__rolling_grid_"
            + site_id
            + ".pdf",
            shell=True,
        )

    return res
