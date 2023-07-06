import os
import janitor
import itertools
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from datetime import timedelta
import statsmodels.formula.api as smf
from numpy_ext import rolling_apply as rolling_apply_ext


def p_interact(x, y):
    dt_sub = pd.DataFrame({"x": x, "y": y})
    dt_sub["period"] = (
        ["before" for _ in range(247)]
        + ["during" for _ in range(70)]
        + ["after" for _ in range(249)]
    )

    if (not any(pd.notna(dt_sub.y.values))) or (not any(pd.notna(dt_sub.x.values))):
        return np.nan

    if (sum(pd.notna(dt_sub.y.values)) < 7) or (sum(pd.notna(dt_sub.x.values)) < 7):
        return np.nan

    try:
        model = smf.ols("np.log(y) ~ x * period", data=dt_sub).fit()
        res = sm.stats.anova_lm(model, typ=1)
        res = res.to_dict()["PR(>F)"]["x:period"]
        return res
    except:  # SVD did not converge. or too much missing data?
        return np.nan


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

    test = rolling_apply_ext(
        p_interact, window_size, dt[indep].values, dt[dep].values, n_jobs=1
    )
    test = test[~np.isnan(test)]

    return (stats.percentileofscore(test, p_fl) / 100, test, dt_event.index[0], p_fl)


def preprocess_dt(file_in, dep_cols, indep_cols, daylight_threshold=100):
    dt = pd.read_csv(
        file_in,
        na_values=["-9999.0"],
    ).clean_names()

    dt = janitor.remove_empty(dt)
    dt["timestamp_start"] = pd.to_datetime(dt["timestamp_start"], format="%Y%m%d%H%M")
    dt["timestamp_end"] = pd.to_datetime(dt["timestamp_end"], format="%Y%m%d%H%M")
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
    else:
        indep_cols = [x for x in indep_cols if x != "ppfd_in"]
        dt = dt[dt["netrad"] > 0]  # daytime

    dt = janitor.remove_empty(dt)
    dep_cols = [x for x in dep_cols if x in dt.columns]
    indep_cols = [x for x in indep_cols if x in dt.columns]

    dt = dt[[x for x in ~dt[dep_cols + indep_cols].isna().all(axis=1)]]

    # dt[dep_cols].head()
    # dt[indep_cols].describe()
    # breakpoint()
    # sum(pd.isna(dt["co2"])) / dt.shape[0]
    for i in range(len(dep_cols)):
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
        # breakpoint()
        grid["pquant"] = None
        for i in range(grid.shape[0]):
            print(i)
            grid["pquant"].iloc[i] = round(
                abs(
                    p_quantile(
                        dt,
                        dt_event,
                        grid.iloc[[i]]["dep"].values[0],
                        grid.iloc[[i]]["indep"].values[0],
                    )[0]
                ),
                2,
            )
        # TODO: why is the processing ending before this line?

        breakpoint()

        grid = grid.sort_values("pquant")
        grid.to_csv(out_path, index=False)
