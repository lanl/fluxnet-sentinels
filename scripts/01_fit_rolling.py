# python scripts/01_fit_rolling.py --site FHK --date_event 2011-03-11 --path_in ../../Data/Asiaflux/FHK.csv --path_out figures/__rolling_fukushima_ --var_dep le --var_idep rh --bearing 45 --tolerance 10 --n_days 7 --uses_letters
#
# python scripts/01_fit_rolling.py --site BE-Lon --date_event 2008-08-23 --path_in ../../Data/Euroflux/BELon.csv --path_out figures/__rolling_fleurus_ --var_dep co2 --var_idep ta --bearing 235 --tolerance 10 --n_days 7
#
import os
import sys
import click
import janitor
import numpy as np
import pandas as pd
import seaborn as sns
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
@click.option("--uses_letters", is_flag=True, default=False)
@click.option("--run_detailed", is_flag=True, default=False)
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
    uses_letters,
    run_detailed,
):
    dep_cols = ["co2", "fc", "le", "h", "co"]
    indep_cols = ["ws", "p", "pa", "rh", "ppfd_in", "ta", "netrad"]

    site_id = site.lower()
    site_code = site_id.replace("-", "")

    dt, dt_select = rolling.preprocess_dt(path_in, dep_cols, indep_cols)
    dt = janitor.remove_empty(dt)
    dt_event = rolling.define_period(dt_select, n_days=n_days, date_event=date_event)

    grid = rolling.make_grid(dt, dep_cols, indep_cols)
    grid = rolling.regression_grid(grid, dt, dt_event, site_id, n_days)

    if not run_detailed:
        return None

    varpair = (var_dep, var_idep)
    varpair_code = "v".join(varpair) + "_"

    path_pdist = "data/pdist_" + varpair_code + site_code + ".csv"
    path_pevent = "data/p_event_" + varpair_code + site_code + ".csv"
    path_event_index = "data/event_index_" + varpair_code + site_code + ".csv"
    if (not os.path.exists(path_pdist)) or (not os.path.exists(path_pevent)):
        _, pdist, timestamps, event_index, p_event = rolling.p_quantile(
            dt, dt_event, varpair[0], varpair[1]
        )
        pd.DataFrame({"timestamp": timestamps, "pdist": pdist}).to_csv(
            path_pdist, index=False
        )
        pd.DataFrame({"pevent": p_event}, index=[0]).to_csv(path_pevent, index=False)
        pd.DataFrame({"event_index": event_index}, index=[0]).to_csv(
            path_event_index, index=False
        )
    pdist = pd.read_csv(path_pdist)
    timestamps = [x for x in pdist["timestamp"]]
    p_event = float(
        pd.read_csv(
            path_pevent,
        ).values[0]
    )
    event_index = float(
        pd.read_csv(
            path_event_index,
        ).values[0]
    )

    plt.close()
    g = sns.histplot(abs(np.log(pdist["pdist"])))
    g.axvline(abs(np.log(p_event)))
    # plt.show()
    print("figures/__" + varpair_code + site_code + "_hist.pdf")
    plt.savefig("figures/__" + varpair_code + site_code + "_hist.pdf")

    wind_fraction = rolling.towards(dt, bearing, tolerance, uses_letters=uses_letters)
    pd.DataFrame({"wind_fraction": wind_fraction}).to_csv(
        "data/wind_fraction.csv", index=False
    )
    g_data = pd.DataFrame(
        {
            "timestamp": timestamps,
            "index": [x for x in range(len(pdist))],
            "p": abs(np.log([x for x in pdist["pdist"]])),
            "wind_fraction": wind_fraction,
        }
    )
    g_data["timestamp"] = pd.to_datetime(g_data["timestamp"])
    tt = [
        (
            g_data.iloc[i]["wind_fraction"]
            >= g_data.iloc[int(event_index)]["wind_fraction"]
        )
        and (g_data.iloc[i]["p"] >= g_data.iloc[int(event_index)]["p"])
        for i in range(g_data.shape[0])
    ]

    plt.close()
    _, ax1 = plt.subplots(figsize=(9, 6))
    g = sns.lineplot(data=g_data, x="timestamp", y="p", ax=ax1)
    g.axvline(pd.to_datetime(date_event), color="yellow")
    g.axhline(abs(np.log(p_event)), color="darkgreen")
    g.set_ylim(0, 60)
    ax1.set_ylabel("effect size (blue line, green line [event])")
    ax1.text(pd.to_datetime(date_event), 3, "<-Event", color="red")

    ax2 = ax1.twinx()
    g2 = sns.lineplot(
        data=g_data, x="timestamp", y="wind_fraction", ax=ax2, color="black"
    )
    g2.set_ylim(-1, 1)
    # g_data.iloc[int(event_index)]["p"]
    [
        g2.axvline(g_data[tt].iloc[i]["timestamp"], color="orange")
        for i in range(g_data[tt].shape[0])
    ]
    # g_data[
    #     (g_data["p"] > abs(np.log(p_event))).values and (g_data["test"] > 0.7).values
    # ].shape
    ax2.set_ylabel("fraction wind towards (black line)")
    plt.suptitle(site + "(" + ",".join(varpair) + ")")
    ax1.set_xlabel("")
    ax2.set_xlabel("")
    # plt.show()
    plt.savefig(path_out + site_code + ".pdf")

    return path_out + site_code + ".pdf"


if __name__ == "__main__":
    fit_rolling()  # pylint: disable=E1120
