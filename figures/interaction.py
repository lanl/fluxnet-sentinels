import sys
import janitor
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt

sys.path.append(".")
from src import rolling


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
fig, ax = plt.subplots(1, 2, figsize=(9, 6))
gg = sns.lmplot(x="ta", y="co2", ci=None, hue="period", data=dt_event)
# sns.regplot(
#     x="ta",
#     y="co2",
#     color="period",
#     ci=None,
#     data=dt_event,
#     # fit_reg=False,
#     # scatter=False,
#     ax=ax[0],
# )
# plt.show()
plt.savefig("figures/interaction.pdf")

# gg = sns.ecdfplot(x=abs(np.log(pdist["pdist"])))
# gg.axvline(abs(np.log(pevent["pevent"].values[0])))
# plt.xscale("log")
# plt.show()

gg = sns.histplot(x=abs(np.log(pdist["pdist"])))
gg.axvline(abs(np.log(pevent["pevent"].values[0])), color="yellow")
plt.xlab("adsf")
plt.show()

model = smf.ols(
    "np.log(" + var_dep + ") ~ " + var_idep + " * period", data=dt_event
).fit()

sm.graphics.interaction_plot(
    dt_event["period"].reset_index(drop=True),
    dt_event["ta"].reset_index(drop=True),
    model.fittedvalues.reset_index(drop=True),
)


p_fl = sm.stats.anova_lm(model, typ=1).to_dict()["PR(>F)"][var_idep + ":period"]

# highlight event interaction

# cdf of interaction effect size?
