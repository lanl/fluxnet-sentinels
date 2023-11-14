import sys
import janitor
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
import statsmodels.formula.api as smf

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


site = "BE-Lon"
site_id = site.lower()
site_code = site_id.replace("-", "")
tolerance = 10
n_days = 7
event_quantile = 0.95
var_dep = "co2"
var_idep = "ta"

path_in = "../../Data/Euroflux/BELon.csv"
dt = pd.read_csv(path_in)

path_slug = (
    site_code + "_" + str(tolerance) + "_" + str(n_days) + "_" + str(event_quantile)
)

varpair = (var_dep, var_idep)
varpair_code = "v".join(varpair) + "_"

path_pdist = "data/pdist_" + varpair_code + path_slug + ".csv"
path_pevent = "data/p_event_" + varpair_code + path_slug + ".csv"
path_event_index = "data/event_index_" + varpair_code + path_slug + ".csv"
pdist = pd.read_csv(path_pdist)
pevent = pd.read_csv(path_pevent)
event_index = pd.read_csv(path_event_index)


# ---

# plot overall interaction on top of individual interaction lines
dep_cols = ["co2", "fc", "le", "h", "co"]
indep_cols = ["ws", "p", "pa", "rh", "ppfd_in", "ta", "netrad"]
date_event = "2008-08-23"

dt, dt_select = rolling.preprocess_dt(path_in, dep_cols, indep_cols)
dt = janitor.remove_empty(dt)
dt_event = rolling.define_period(dt_select, n_days=n_days, date_event=date_event)

plt.close()
fig, (ax1, ax2) = plt.subplots(1, 2)
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
    x=abs(np.log(pdist["pdist"])),
    element="step",
    edgecolor="gray",
    color="gray",
    ax=ax2,
)
gg2.axvline(abs(np.log(pevent["pevent"].values[0])), color="orange")
ax2.set_xlabel("Effect size")
plt.suptitle("BE-Lon\nlog(co2) ~ ta * period")
plt.tight_layout()
# plt.show()
plt.savefig("figures/__interaction.pdf", bbox_inches="tight", pad_inches=0.1)

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
