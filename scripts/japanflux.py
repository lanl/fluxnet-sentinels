import os
import janitor
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def preprocess_dt(file_in):
    # file_in = "../../Data/Asiaflux/FxMt_FHK_2011_30m_02/FxMt_FHK_2011_30m_02.csv"
    os.path.exists(file_in)

    names = pd.read_csv(file_in, nrows=1, encoding="Shift_JIS").clean_names()

    dt = pd.read_csv(
        file_in,
        skiprows=1,
        encoding="Shift_JIS",
        na_values=["-9999.0"],
    )
    dt.columns = [x for x in names.columns]
    dt = janitor.remove_empty(dt)
    dt["i"] = [x for x in range(dt.shape[0])]

    return dt


# ---

file_in = "../../Data/Asiaflux/FxMt_FHK_2011_30m_02/FxMt_FHK_2011_30m_02.csv"
dt_2011 = preprocess_dt(file_in)

file_in = "../../Data/Asiaflux/FxMt_FHK_2010_30m_02/FxMt_FHK_2010_30m_02.csv"
dt_2010 = preprocess_dt(file_in)

file_in = "../../Data/Asiaflux/FxMt_FHK_2012_30m_02/FxMt_FHK_2012_30m_02.csv"
dt_2012 = preprocess_dt(file_in)

dt = pd.concat(
    [
        dt_2010[["year", "nee", "co", "i"]],
        dt_2011[["year", "nee", "co", "i"]],
        dt_2012[["year", "nee", "co", "i"]],
    ]
).reset_index(drop=True)
dt = dt[dt["year"] < 2013]

# ---

g = sns.relplot(data=dt, x="i", y="nee", row="year", hue="year", kind="line")
g.refline(x=3314)
plt.savefig("figures/__japanflux_nee.pdf")

g = sns.relplot(data=dt, x="i", y="co", row="year", hue="year", kind="line")
g.refline(x=3314)
plt.savefig("figures/__japanflux_co.pdf")
