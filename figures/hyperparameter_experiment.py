import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

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

sns.lmplot(x="value", y="false_positive_rate", col="variable", sharex=False, data=dt)
plt.savefig("figures/__hyperparameter_experiment.pdf")
