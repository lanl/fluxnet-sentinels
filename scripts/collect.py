import glob
import itertools
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def parse_f(f_i):
    # f_i = flist[0]
    f_i = f_i.replace(".csv", "")
    f_i = f_i.split("_")
    (tolerance, n_days, event_quantile) = tuple(f_i[(len(f_i) - 3) : len(f_i)])
    return {"tolerance": tolerance, "n_days": n_days, "event_quantile": event_quantile}


flist = glob.glob("data/p_event*")
flist = list(itertools.compress(flist, [len(f_i) > 30 for f_i in flist]))

dt = [pd.DataFrame(parse_f(flist[i]), index=[0]) for i in range(len(flist))]
dt = pd.concat(dt)
dt["p_event"] = [pd.read_csv(flist[i])["pevent"][0] for i in range(len(flist))]

sns.lmplot()
plt.show()
