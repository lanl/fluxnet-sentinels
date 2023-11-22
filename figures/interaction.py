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


def hue_regplot(data, x, y, hue, palette=None, **kwargs):
    """
    https://stackoverflow.com/a/63755041
    """

    regplots = []

    levels = data[hue].unique()

    if palette is None:
        default_colors = get_cmap("tab10")
        palette = {k: default_colors(i) for i, k in enumerate(levels)}

    for key in levels:
        regplots.append(
            sns.regplot(
                x=x, y=y, data=data[data[hue] == key], color=palette[key], **kwargs
            )
        )

    return regplots


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

plt.close()
fig, axs = plt.subplots(2, 2)
ax1, ax2, ax3, ax4 = axs[0, 0], axs[0, 1], axs[1, 0], axs[1, 1]
gg1 = hue_regplot(data=dt_event, x="ta", y="co2", hue="period", ax=ax1, ci=None)
colors = sns.color_palette(n_colors=3).as_hex()
legend_elements = [
    Line2D([0], [0], color=colors[0], lw=4, label="Before"),
    Line2D([0], [0], color=colors[1], lw=4, label="During"),
    Line2D([0], [0], color=colors[2], lw=4, label="After"),
]
ax1.legend(handles=legend_elements, loc="upper right")
#
gg2 = sns.histplot(
    x=pfdist["fdist"],
    element="step",
    edgecolor="gray",
    color="gray",
    ax=ax2,
)
gg2.axvline(fevent["fevent"].values[0], color="orange")
ax2.set_xlabel("Effect size")
#
timestamps = [x for x in pfdist["timestamp"]]
ts_start = timestamps[
    int(np.where([x == np.nanmin(pfdist["fdist"]) for x in pfdist["fdist"]])[0][0])
]
dt_event_weak = rolling.define_period(dt_select, n_days=n_days, date_event=ts_start)
gg3 = hue_regplot(data=dt_event_weak, x="ta", y="co2", hue="period", ax=ax3, ci=None)
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
ax4.set_xlabel("Effect size")
#
plt.suptitle("BE-Lon\nlog(" + var_dep + ") ~ " + var_idep + " * period")
plt.tight_layout()
# plt.show()
plt.savefig("figures/__interaction_belon.pdf", bbox_inches="tight", pad_inches=0.1)

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
