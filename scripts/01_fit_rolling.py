"""
    Fitting a rolling interaction model first of all pairs then of a specified variable pair
"""
# tolerance: the spread around the specified bearing indicating what counts as "towards"
# n_days: the number of days to count as included in the event
# event_quantile: how extreme within the event window do we count as an abnormal event?
# effect size: prespecify an effect size rather than calculate from the event?
# run_detailed: run a specified idep/dep pair analysis or only a general overview?
#
# python scripts/01_fit_rolling.py --site FHK --date_event 2011-03-11 --path_in ../../Data/Asiaflux/FHK.csv --path_out figures/__rolling_fukushima_ --var_dep le --var_idep rh --bearing 45 --tolerance 10 --n_days 7 --uses_letters --run_detailed
#
# python scripts/01_fit_rolling.py --site BE-Lon --date_event 2008-08-23 --path_in ../../Data/Euroflux/BELon.csv --path_out figures/__rolling_fleurus_ --var_dep co2 --var_idep ta --bearing 235 --tolerance 10 --n_days 7  --event_quantile_wind 0.7 --event_quantile_effect 0.9 --run_detailed --overwrite
#
# python scripts/01_fit_rolling.py --site BE-Bra --date_event 2008-08-23 --path_in ../../Data/Euroflux/BEBra.csv --path_out figures/__rolling_fleurus_ --var_dep co2 --var_idep ta --bearing 180 --tolerance 10 --n_days 7  --event_quantile_wind 0.7 --event_quantile_effect 0.9 --run_detailed --overwrite
#
# python scripts/01_fit_rolling.py --site BE-Vie --date_event 2008-08-23 --path_in ../../Data/Euroflux/BEVie.csv --path_out figures/__rolling_fleurus_ --var_dep co2 --var_idep ta --bearing 235 --tolerance 10 --n_days 7  --event_quantile_wind 0.7 --event_quantile_effect 0.9 --run_detailed --overwrite
#
import os
import sys
import click
import janitor
import numpy as np
import pandas as pd
import seaborn as sns
from datetime import datetime
import matplotlib.pyplot as plt


sys.path.append(".")
from src import rolling


@click.command()
@click.option("--site")
@click.option("--date_event")
@click.option("--path_in")
@click.option("--path_out")
@click.option("--var_dep")
@click.option("--var_idep")
@click.option("--bearing", type=int)
@click.option("--tolerance", type=int)
@click.option("--n_days", type=int)
@click.option("--event_quantile_wind", type=float)
@click.option("--event_quantile_effect", type=float)
@click.option("--event_effect", type=float, default=None)
@click.option("--event_wind", type=float, default=None)
@click.option("--uses_letters", is_flag=True, default=False)
@click.option("--run_detailed", is_flag=True, default=False)
@click.option("--overwrite", is_flag=True, default=False)
@click.option("--no_false_positives", is_flag=True, default=False)
def fit_rolling(
    site,
    date_event,
    path_in,
    path_out,
    var_dep,
    var_idep,
    bearing,
    tolerance,
    n_days,
    event_quantile_wind,
    event_quantile_effect,
    uses_letters,
    run_detailed,
    overwrite,
    event_effect=None,
    event_wind=None,
    no_false_positives=False,
):
    # --- setup
    dep_cols = ["co2", "fc", "le", "h", "co"]
    indep_cols = ["ws", "p", "pa", "rh", "ppfd_in", "ta", "netrad"]

    site_id = site.lower()
    site_code = site_id.replace("-", "")

    varpair = (var_dep, var_idep)
    varpair_code = "v".join(varpair) + "_"

    path_slug = (
        site_code
        + "_"
        + varpair_code
        + str(tolerance)
        + "_"
        + str(n_days)
        + "_"
        + str(event_quantile_effect)
    )
    path_fig = path_out + path_slug + ".pdf"
    if os.path.exists(path_fig) and not overwrite:
        print("'" + path_fig + "' already exists, exiting...")
        return None

    # --- grid pair-wise analysis
    dt, dt_select = rolling.preprocess_dt(path_in, dep_cols, indep_cols)
    dt = janitor.remove_empty(dt)
    dt_event = rolling.define_period(dt_select, n_days=n_days, date_event=date_event)
    window_size = dt_event.shape[0]

    grid = rolling.make_grid(dt, dep_cols, indep_cols)
    grid = rolling.regression_grid(
        grid,
        dt,
        dt_event,
        site_id,
        n_days,
        overwrite=False,
        window_size=window_size,
    )

    if not run_detailed:
        return None

    # --- detailed single pair analysis
    path_pfdist = "data/pfdist_" + path_slug + ".csv"
    path_pevent = "data/p_event_" + path_slug + ".csv"
    path_fevent = "data/f_event_" + path_slug + ".csv"
    path_r2event = "data/r2_event_" + path_slug + ".csv"
    path_event_index = "data/event_index_" + path_slug + ".csv"
    if (not os.path.exists(path_pfdist)) or (not os.path.exists(path_r2event)):
        (
            _,
            pdist,
            fdist,
            timestamps,
            event_index,
            p_event,
            f_event,
            r2_event,
        ) = rolling.p_quantile(dt, dt_event, varpair[0], varpair[1], window_size)
        pd.DataFrame({"timestamp": timestamps, "pdist": pdist, "fdist": fdist}).to_csv(
            path_pfdist, index=False
        )
        pd.DataFrame({"pevent": p_event}, index=[0]).to_csv(path_pevent, index=False)
        pd.DataFrame({"fevent": f_event}, index=[0]).to_csv(path_fevent, index=False)
        pd.DataFrame({"r2event": r2_event}, index=[0]).to_csv(path_r2event, index=False)
        pd.DataFrame({"event_index": event_index}, index=[0]).to_csv(
            path_event_index, index=False
        )
    pfdist = pd.read_csv(path_pfdist)
    timestamps = [x for x in pfdist["timestamp"]]
    p_event = float(
        pd.read_csv(
            path_pevent,
        ).values[0]
    )
    f_event = float(
        pd.read_csv(
            path_fevent,
        ).values[0]
    )
    r2_event = float(
        pd.read_csv(
            path_r2event,
        ).values[0]
    )
    event_index = float(
        pd.read_csv(
            path_event_index,
        ).values[0]
    )

    wind_fraction = rolling.towards(
        dt, bearing, tolerance, uses_letters=uses_letters, window_size=window_size
    )
    pd.DataFrame({"wind_fraction": wind_fraction}).to_csv(
        "data/wind_fraction.csv", index=False
    )
    g_data = pd.DataFrame(
        {
            "timestamp": timestamps,
            "index": [x for x in range(len(pfdist))],
            "p": abs(np.log([x for x in pfdist["pdist"]])),
            "wind_fraction": wind_fraction,
            "F": [x for x in pfdist["fdist"]],
        }
    )
    g_data["timestamp"] = pd.to_datetime(g_data["timestamp"])
    if event_wind is None:
        event_wind = np.quantile(
            [
                g_data.iloc[int(event_index + i)]["wind_fraction"]
                for i in range(2 * 24 * n_days)  # half-hourly data
            ],
            [event_quantile_wind],
        )[0]
    if event_effect is None:
        event_effect = np.quantile(
            [g_data.iloc[int(event_index + i)]["F"] for i in range(2 * 24 * n_days)],
            [event_quantile_effect],
        )[0]

    tt = [
        (g_data.iloc[i]["wind_fraction"] >= event_wind)
        and (g_data.iloc[i]["F"] >= event_effect)
        for i in range(g_data.shape[0])
    ]
    false_positive_rate = round(sum(tt) / g_data.shape[0], 2)
    if sum(tt) == 0:
        false_positive_rate = "NA"

    # --- plotting
    plt.close()
    g = sns.histplot(abs(np.log(pfdist["pdist"])))
    g.axvline(abs(np.log(p_event)))
    # plt.show()
    print("figures/__" + varpair_code + site_code + "_hist.pdf")
    plt.savefig("figures/__" + varpair_code + site_code + "_hist.pdf")

    plt.close()
    _, ax1 = plt.subplots(figsize=(9, 6))
    g = sns.lineplot(data=g_data, x="timestamp", y="F", ax=ax1)
    g.axvline(pd.to_datetime(date_event), color="yellow")
    g.axhline(abs(np.log(p_event)), color="darkgreen")
    g.set_ylim(0, np.nanquantile(g_data["F"], [1]) + 10)
    ax1.set_ylabel("effect size (blue line, green line [event])")
    ax1.text(pd.to_datetime(date_event), 3, "<-Event", color="red")

    ax2 = ax1.twinx()
    g2 = sns.lineplot(
        data=g_data, x="timestamp", y="wind_fraction", ax=ax2, color="black"
    )
    g2.set_ylim(-1, 1)
    # g_data.iloc[int(event_index)]["p"]
    if not no_false_positives:
        [
            g2.axvline(g_data[tt].iloc[i]["timestamp"], color="orange")
            for i in range(g_data[tt].shape[0])
        ]
    # g_data[
    #     (g_data["p"] > abs(np.log(p_event))).values and (g_data["test"] > 0.7).values
    # ].shape
    ax2.set_ylabel("fraction wind towards (black line)")
    plt.suptitle(
        site
        + "("
        + ",".join(varpair)
        + ")"
        + r"$\alpha$"
        + "="
        + str(false_positive_rate)
    )
    ax1.set_xlabel("")
    ax2.set_xlabel("")
    # plt.show()
    print(path_fig)
    plt.savefig(path_fig)

    # ---
    log_info = pd.DataFrame(
        {
            "date": str(datetime.now()),
            "site": site,
            "wind_tolerance": tolerance,
            "n_days": n_days,
            "event_quantile_effect": event_quantile_effect,
            "false_positive_rate": false_positive_rate,
            "event_effect": event_effect,
            "event_wind": event_wind,
            "event_r2": r2_event,
        },
        index=[0],
    )
    print(log_info.T)
    log_info.to_csv("data/log.csv", mode="a", header=False, index=False)

    return log_info


if __name__ == "__main__":
    fit_rolling()  # pylint: disable=E1120
