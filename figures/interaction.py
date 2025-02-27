import sys
import janitor
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
from matplotlib.lines import Line2D

sys.path.append(".")
from src import rolling

plt.rcParams["text.usetex"] = True


def hue_regplot(data, x, y, hue, palette=None, **kwargs):
    """
    https://stackoverflow.com/a/63755041
    """

    regplots = []

    levels = data[hue].unique()

    if palette is None:
        default_colors = get_cmap("Dark2")
        palette = {k: default_colors(i) for i, k in enumerate(levels)}

    for key in levels:
        regplots.append(
            sns.regplot(
                x=x,
                y=y,
                data=data[data[hue] == key],
                color=palette[key],
                marker="$\circ$",
                **kwargs
            )
        )

    return regplots


def interaction_plot(
    dt_event,
    var_idep,
    var_dep,
    ylab,
    xlab,
    pfdist,
    fevent,
    dt_select,
    n_days,
    ts_start,
    out_path,
):
    plt.close()
    _, axs = plt.subplots(2, 2)
    ax1, ax2, ax3, ax4 = axs[0, 0], axs[0, 1], axs[1, 0], axs[1, 1]
    #
    gg1 = hue_regplot(
        data=dt_event, x=var_idep, y=var_dep, hue="period", ax=ax1, ci=None
    )
    colors = sns.color_palette(palette="Dark2", n_colors=3).as_hex()
    legend_elements = [
        Line2D([0], [0], color=colors[0], lw=4, label="Before"),
        Line2D([0], [0], color=colors[1], lw=4, label="During"),
        Line2D([0], [0], color=colors[2], lw=4, label="After"),
    ]
    ax1.legend(handles=legend_elements, loc="upper right")
    ax1.set_ylabel(ylab)
    ax1.set_xlabel(xlab)
    ax1.set_title("A.", pad=0, x=0.07, y=0.9)
    #
    gg2 = sns.histplot(
        x=pfdist["fdist"],
        element="step",
        edgecolor="gray",
        color="gray",
        ax=ax2,
    )
    gg2.axvline(fevent["fevent"].values[0], color="orange")
    gg2.set_xlim(-2, 150)
    ax2.set_xlabel("Effect size")
    ax2.set_title("C.", pad=0, x=0.07, y=0.9)
    #
    dt_event_weak = rolling.define_period(dt_select, n_days=n_days, date_event=ts_start)
    gg3 = hue_regplot(
        data=dt_event_weak, x="ta", y="co2", hue="period", ax=ax3, ci=None
    )
    ax3.set_ylabel(ylab)
    ax3.set_xlabel(xlab)
    ax3.set_title("B.", pad=0, x=0.07, y=0.9)
    #
    # stats.percentileofscore(pfdist["fdist"], fevent["fevent"], nan_policy="omit") / 100
    gg4 = sns.histplot(
        x=pfdist["fdist"],
        element="step",
        edgecolor="gray",
        color="gray",
        ax=ax4,
    )
    gg4.axvline(np.nanmin(pfdist["fdist"]), color="orange")
    gg4.set_xlim(-2, 150)
    ax4.set_xlabel("Effect size")
    ax4.set_title("D.", pad=0, x=0.07, y=0.9)
    #
    # plt.suptitle("BE-Lon\nlog(" + var_dep + ") ~ " + var_idep + " * period")
    plt.tight_layout()
    # plt.show()
    plt.savefig(out_path, bbox_inches="tight", pad_inches=0.1)


# --- BE-Lon
# python scripts/01_fit_rolling.py --site BE-Lon --date_event 2008-08-23 --path_in ../../Data/Euroflux/BELon.csv --path_out figures/__rolling_fleurus_ --var_dep fc --var_idep netrad --bearing 235 --tolerance 10 --n_days 7 --event_quantile 0.9 --run_detailed

site = "BE-Lon"
site_id = site.lower()
site_code = site_id.replace("-", "")
tolerance = 10
n_days = 7
event_quantile = 0.9
var_dep = "co2"
var_idep = "ta"
ylab = "$CO_2$ (ppm)"
xlab = r"Temperature ($^{\circ}$C)"
# var_dep = "fc"
# var_idep = "netrad"

path_in = "../../Data/Euroflux/BELon.csv"
dt = pd.read_csv(path_in)

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
    + str(event_quantile)
)

path_pfdist = "data/pfdist_" + path_slug + ".csv"
path_fevent = "data/f_event_" + path_slug + ".csv"
path_event_index = "data/event_index_" + path_slug + ".csv"
pfdist = pd.read_csv(path_pfdist)
fevent = pd.read_csv(path_fevent)
event_index = pd.read_csv(path_event_index)

dep_cols = ["co2", "fc", "le", "h", "co"]
indep_cols = ["ws", "p", "pa", "rh", "ppfd_in", "ta", "netrad"]
date_event = "2008-08-23"

dt, dt_select = rolling.preprocess_dt(path_in, dep_cols, indep_cols)
dt = janitor.remove_empty(dt)
dt_event = rolling.define_period(dt_select, n_days=n_days, date_event=date_event)

# limit ts_start to the same month as date_event
pfdist["month"] = [x.month for x in pd.to_datetime(pfdist["timestamp"])]
# avoid 2009 because of missing data
pfdist["year"] = [x.year for x in pd.to_datetime(pfdist["timestamp"])]
pfdist_temp = pfdist[pfdist["year"] != 2009]
pfdist_temp = pfdist_temp[pfdist_temp["year"] != 2008]
pfdist_temp = pfdist_temp.sort_values("fdist", ascending=True)
pfdist_temp = pfdist_temp[pfdist_temp["month"] == pd.to_datetime(date_event).month]
ts_start = pfdist_temp["timestamp"].iloc[[0]].values[0]

interaction_plot(
    dt_event,
    var_idep,
    var_dep,
    ylab,
    xlab,
    pfdist,
    fevent,
    dt_select,
    n_days,
    ts_start,
    "figures/__interaction_belon.pdf",
)

# --- BE-Bra
site = "BE-Bra"
site_id = site.lower()
site_code = site_id.replace("-", "")
tolerance = 10
n_days = 7
event_quantile = 0.9
var_dep = "co2"
var_idep = "ta"
ylab = "$CO_2$ (ppm)"
xlab = r"Temperature ($^{\circ}$C)"
# var_dep = "fc"
# var_idep = "netrad"

path_in = "../../Data/Euroflux/BEBra.csv"
dt = pd.read_csv(path_in)

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
    + str(event_quantile)
)

path_pfdist = "data/pfdist_" + path_slug + ".csv"
path_fevent = "data/f_event_" + path_slug + ".csv"
path_event_index = "data/event_index_" + path_slug + ".csv"
pfdist = pd.read_csv(path_pfdist)
fevent = pd.read_csv(path_fevent)
event_index = pd.read_csv(path_event_index)

dep_cols = ["co2", "fc", "le", "h", "co"]
indep_cols = ["ws", "p", "pa", "rh", "ppfd_in", "ta", "netrad"]
date_event = "2008-08-23"

dt, dt_select = rolling.preprocess_dt(path_in, dep_cols, indep_cols)
dt = janitor.remove_empty(dt)
dt_event = rolling.define_period(dt_select, n_days=n_days, date_event=date_event)

# limit ts_start to the same month as date_event
pfdist["month"] = [x.month for x in pd.to_datetime(pfdist["timestamp"])]
# avoid 2009 because of missing data
pfdist["year"] = [x.year for x in pd.to_datetime(pfdist["timestamp"])]
pfdist_temp = pfdist[pfdist["year"] != 2009]
pfdist_temp = pfdist_temp[pfdist_temp["year"] != 2008]
pfdist_temp = pfdist_temp.sort_values("fdist", ascending=True)
pfdist_temp = pfdist_temp[pfdist_temp["month"] == pd.to_datetime(date_event).month]
ts_start = pfdist_temp["timestamp"].iloc[[0]].values[0]

interaction_plot(
    dt_event,
    var_idep,
    var_dep,
    ylab,
    xlab,
    pfdist,
    fevent,
    dt_select,
    n_days,
    ts_start,
    "figures/__interaction_bebra.pdf",
)

# --- BE-Bra
site = "BE-Vie"
site_id = site.lower()
site_code = site_id.replace("-", "")
tolerance = 10
n_days = 7
event_quantile = 0.9
var_dep = "co2"
var_idep = "ta"
ylab = "$CO_2$ (ppm)"
xlab = r"Temperature ($^{\circ}$C)"
# var_dep = "fc"
# var_idep = "netrad"

path_in = "../../Data/Euroflux/BEVie.csv"
dt = pd.read_csv(path_in)

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
    + str(event_quantile)
)

path_pfdist = "data/pfdist_" + path_slug + ".csv"
path_fevent = "data/f_event_" + path_slug + ".csv"
path_event_index = "data/event_index_" + path_slug + ".csv"
pfdist = pd.read_csv(path_pfdist)
fevent = pd.read_csv(path_fevent)
event_index = pd.read_csv(path_event_index)

dep_cols = ["co2", "fc", "le", "h", "co"]
indep_cols = ["ws", "p", "pa", "rh", "ppfd_in", "ta", "netrad"]
date_event = "2008-08-23"

dt, dt_select = rolling.preprocess_dt(path_in, dep_cols, indep_cols)
dt = janitor.remove_empty(dt)
dt_event = rolling.define_period(dt_select, n_days=n_days, date_event=date_event)

# limit ts_start to the same month as date_event
pfdist["month"] = [x.month for x in pd.to_datetime(pfdist["timestamp"])]
# avoid 2009 because of missing data
pfdist["year"] = [x.year for x in pd.to_datetime(pfdist["timestamp"])]
pfdist_temp = pfdist[pfdist["year"] != 2009]
pfdist_temp = pfdist_temp[pfdist_temp["year"] != 2008]
pfdist_temp = pfdist_temp.sort_values("fdist", ascending=True)
pfdist_temp = pfdist_temp[pfdist_temp["month"] == pd.to_datetime(date_event).month]
ts_start = pfdist_temp["timestamp"].iloc[[10]].values[0]

interaction_plot(
    dt_event,
    var_idep,
    var_dep,
    ylab,
    xlab,
    pfdist,
    fevent,
    dt_select,
    n_days,
    ts_start,
    "figures/__interaction_bevie.pdf",
)

# --- US-Wrc
# python scripts/01_fit_rolling.py --site US-Wrc --date_event 2011-03-11 ...
# breakpoint()
site = "US-Wrc"
site_id = site.lower()
site_code = site_id.replace("-", "")
tolerance = 45
n_days = 7
event_quantile = 0.9
var_dep = "le"
var_idep = "rh"
ylab = "Latent Heat"
xlab = "Relative Humidity"

path_in = "../../Data/ameriflux/US-Wrc.csv"
dt = pd.read_csv(path_in)

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
    + str(event_quantile)
)

path_pfdist = "data/pfdist_" + path_slug + ".csv"
path_fevent = "data/f_event_" + path_slug + ".csv"
path_event_index = "data/event_index_" + path_slug + ".csv"
pfdist = pd.read_csv(path_pfdist)
fevent = pd.read_csv(path_fevent)
event_index = pd.read_csv(path_event_index)

dep_cols = ["co2", "fc", "le", "h", "co"]
indep_cols = ["ws", "p", "pa", "rh", "ppfd_in", "ta", "netrad"]
date_event = "2011-03-11"

dt, dt_select = rolling.preprocess_dt(path_in, dep_cols, indep_cols)
dt = janitor.remove_empty(dt)
dt_event = rolling.define_period(dt_select, n_days=n_days, date_event=date_event)

# limit ts_start to the same month as date_event
pfdist["month"] = [x.month for x in pd.to_datetime(pfdist["timestamp"])]
# avoid 2009 because of missing data
pfdist["year"] = [x.year for x in pd.to_datetime(pfdist["timestamp"])]
pfdist_temp = pfdist
# pfdist_temp = pfdist[pfdist["year"] != 2009]
# pfdist_temp = pfdist_temp[pfdist_temp["year"] != 2011]
pfdist_temp = pfdist_temp.sort_values("fdist", ascending=True)
pfdist_temp = pfdist_temp[pfdist_temp["month"] == pd.to_datetime(date_event).month]
ts_start = pfdist_temp["timestamp"].iloc[[40]].values[0]

interaction_plot(
    dt_event,
    var_idep,
    var_dep,
    ylab,
    xlab,
    pfdist,
    fevent,
    dt_select,
    n_days,
    ts_start,
    "figures/__interaction_uswrc.pdf",
)

# ---
# model = smf.ols(
#     "np.log(" + var_dep + ") ~ " + var_idep + " * period", data=dt_event
# ).fit()

# sm.graphics.interaction_plot(
#     dt_event["period"].reset_index(drop=True),
#     dt_event["ta"].reset_index(drop=True),
#     model.fittedvalues.reset_index(drop=True),
# )


# p_fl = sm.stats.anova_lm(model, typ=1).to_dict()["PR(>F)"][var_idep + ":period"]

# highlight event interaction

# cdf of interaction effect size?
