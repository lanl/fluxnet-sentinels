import janitor
import itertools
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

dt = pd.read_csv(
    "../../Data/Euroflux/BE-Lon/L2-L4_2004-2012/EFDC_L2_Flx_BELon_2008_v017_30m.txt",
    na_values=["-9999.0"],
).clean_names()
dt = janitor.remove_empty(dt)
dt["timestamp_start"] = pd.to_datetime(dt["timestamp_start"], format="%Y%m%d%H%M")
dt["timestamp_end"] = pd.to_datetime(dt["timestamp_end"], format="%Y%m%d%H%M")
dt["hour"] = [int(x.strftime("%H")) for x in dt["timestamp_start"]]

dt = dt[dt["netrad"] > 0 ] # daytime

dt.columns

dep_cols = ["co2", "fc", "le", "h"]
indep_cols = ["ws", "p", "pa", "netrad", "rh", "ppfd_in", "ta"]
# dt[dep_cols].head()
# dt[indep_cols].describe()

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
grid = grid.pivot("dep", "indep", values="r2")

ax = sns.heatmap(grid, annot=True)
ax.set(xlabel="", ylabel="")
ax.xaxis.tick_top()
# plt.show()
plt.close()

dt_select = dt[dep_cols + indep_cols]
sns.pairplot(dt_select, x_vars = indep_cols, y_vars = dep_cols)
# plt.show()
plt.close()

sns.lineplot(data=dt, x="timestamp_start", y="wd")
plt.show()

sns.lineplot(data=dt, x="timestamp_start", y="netrad")
plt.show()

sns.regplot(data=dt, x="hour", y="netrad")
plt.show()

# --- define before, during, and after periods
# 10 days before and after
# Before: Aug 12, 13, 14, 15, 16, 17, 18, 19, 20, 21
# During: Aug 22, 23, 24
# After: Aug 25, 26, 27, 28, 29, 30, 31, 1,2,3
dt["period"] = None
dt.loc[
    (dt["timestamp_end"] < pd.to_datetime("2008-08-22"))
    & (dt["timestamp_start"] > pd.to_datetime("2008-08-11")),
    "period",
] = "before"
dt.loc[
    (dt["timestamp_end"] < pd.to_datetime("2008-08-25"))
    & (dt["timestamp_start"] > pd.to_datetime("2008-08-21")),
    "period",
] = "during"
dt.loc[
    dt["timestamp_start"] > pd.to_datetime("2008-08-24"),
    "period",
] = "after"

dt[["timestamp_start", "timestamp_end", "period"]].tail(20)
