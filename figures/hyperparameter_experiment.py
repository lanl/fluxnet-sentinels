import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def set_labels(fig, i, xlab):
    a1 = fig.axes[i]
    a1.set_title("")
    a1.set_xlabel(xlab)


dt = pd.read_csv("data/log_hyperparameter.csv", header=None)
colnames = [
    "date",
    "site",
    "wind_tolerance",
    "n_days",
    "event_quantile_effect",
    "false_positive_rate",
    "event_effect",
    "event_wind",
    "event_r2",
]
dt.columns = colnames
dt = dt.drop(["date", "site"], axis=1)
dt = dt[["false_positive_rate", "wind_tolerance", "n_days", "event_quantile_effect"]]
dt = dt.melt(id_vars="false_positive_rate")

sns.set_theme(font_scale=1.5, style="ticks", palette=["black"])
ax = sns.lmplot(
    x="value",
    y="false_positive_rate",
    col="variable",
    sharex=False,
    data=dt,
    y_jitter=0.003,
)

fig = ax.fig
xlabs = ["Wind tolerance", "Days (n)", "Effect Quantile"]
[set_labels(fig, i, xlabs[i]) for i in range(len(fig.axes))]

# ax.set_xlabels("")
ax.set_ylabels("Event detection rate")
plt.savefig("figures/__hyperparameter_experiment.pdf")
