import os
import janitor
import tabulate
import itertools
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
import statsmodels.api as sm
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
from numpy_ext import rolling_apply as rolling_apply_ext


def p_interact(x, y):
    dt_sub = pd.DataFrame({"x": x, "y": y})
    dt_sub["period"] = (
        ["before" for i in range(247)]
        + ["during" for i in range(70)]
        + ["after" for i in range(249)]
    )
    model = smf.ols("np.log(y) ~ x * period", data=dt_sub).fit()
    return sm.stats.anova_lm(model, typ=1).to_dict()["PR(>F)"]["x:period"]


dt = pd.read_csv(
    "../../Data/Euroflux/BE-Lon/L2-L4_2004-2012/EFDC_L2_Flx_BELon_2008_v017_30m.txt",
    na_values=["-9999.0"],
).clean_names()
dt = janitor.remove_empty(dt)
dt["timestamp_start"] = pd.to_datetime(dt["timestamp_start"], format="%Y%m%d%H%M")
dt["timestamp_end"] = pd.to_datetime(dt["timestamp_end"], format="%Y%m%d%H%M")
dt["hour"] = [int(x.strftime("%H")) for x in dt["timestamp_start"]]

dt = dt[dt["ppfd_in"] > 100]  # daytime

# dt.columns
dep_cols = ["co2", "fc", "le", "h"]
indep_cols = ["ws", "p", "pa", "rh", "ppfd_in", "ta"]
# dt[dep_cols].head()
# dt[indep_cols].describe()
dt[dep_cols[1]] = dt[dep_cols[1]] + abs(min(dt[dep_cols[1]])) + 0.01
dt[dep_cols[2]] = dt[dep_cols[2]] + abs(min(dt[dep_cols[2]])) + 0.01
dt[dep_cols[3]] = dt[dep_cols[3]] + abs(min(dt[dep_cols[3]])) + 0.01

dt_select = dt[["timestamp_start", "timestamp_end"] + dep_cols + indep_cols]

min(dt[dep_cols[3]])

grid = pd.DataFrame(
    list(itertools.product(dep_cols, indep_cols)), columns=["dep", "indep"]
)
grid["r2"] = [
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
    for i in range(grid.shape[0])
]

ax = sns.heatmap(grid.pivot("dep", "indep", values="r2"), annot=True)
ax.set(xlabel="", ylabel="")
ax.xaxis.tick_top()
plt.suptitle("Regression R2")
plt.savefig("figures/__rolling_heatmap.pdf")
plt.close()

sns.pairplot(dt_select, x_vars=indep_cols, y_vars=dep_cols)
# plt.show()
plt.close()

sns.lineplot(data=dt, x="timestamp_start", y="wd")
# plt.show()

sns.lineplot(data=dt, x="timestamp_start", y="netrad")
# plt.show()

sns.regplot(data=dt, x="hour", y="netrad")
# plt.show()

# --- define before, during, and after periods
# 10 days before and after
# Before: Aug 12, 13, 14, 15, 16, 17, 18, 19, 20, 21
# During: Aug 22, 23, 24
# After: Aug 25, 26, 27, 28, 29, 30, 31, 1,2,3
dt_select["period"] = None
dt_select.loc[
    (dt_select["timestamp_end"] < pd.to_datetime("2008-08-22"))
    & (dt_select["timestamp_start"] > pd.to_datetime("2008-08-11")),
    "period",
] = "before"
dt_select.loc[
    (dt_select["timestamp_end"] < pd.to_datetime("2008-08-25"))
    & (dt_select["timestamp_start"] > pd.to_datetime("2008-08-21")),
    "period",
] = "during"
dt_select.loc[
    (dt_select["timestamp_start"] > pd.to_datetime("2008-08-24"))
    & (dt_select["timestamp_start"] < pd.to_datetime("2008-09-04")),
    "period",
] = "after"
dt_event = dt_select[[x is not None for x in dt_select["period"]]].copy()

# ---


def p_quantile(dep, indep):
    # dep = "fc"
    # indep = "ws"
    print((dep, indep))
    model = smf.ols("np.log(" + dep + ") ~ " + indep + " * period", data=dt_event).fit()
    p_fl = sm.stats.anova_lm(model, typ=1).to_dict()["PR(>F)"][indep + ":period"]

    # dt_event["period"].value_counts()
    test = rolling_apply_ext(p_interact, 566, dt[indep].values, dt[dep].values)
    test = test[~np.isnan(test)]
    return stats.percentileofscore(test, p_fl) / 100


# p_quantile("co2", "ta") # ~ 0.14
# p_quantile("fc", "ws")

if not os.path.exists("data/grid.csv"):
    grid["pquant"] = [
        round(
            abs(
                p_quantile(
                    grid.iloc[[i]]["dep"].values[0], grid.iloc[[i]]["indep"].values[0]
                )
            ),
            2,
        )
        for i in range(grid.shape[0])
    ]

    grid = grid.sort_values("pquant")
    grid.to_csv("data/grid.csv", index=False)

grid = pd.read_csv("data/grid.csv")
test = grid[grid["r2"] > 0.05].reset_index(drop=True)

mdtable = tabulate.tabulate(
    test,
    headers=["Explanatory", "Regressor", "R2", r"Event Percentile"],
    tablefmt="simple",
    showindex=False,
)
with open("mdtable.md", "w") as f:
    f.write(mdtable)

# ---

# dep = grid["dep"][0]
# indep = grid["indep"][0]

sns.lmplot(x="ta", y="co2", hue="period", data=dt_event, scatter_kws={"s": 1})
# plt.yscale("log")
# plt.show()
min(dt_event["ppfd_in"])
