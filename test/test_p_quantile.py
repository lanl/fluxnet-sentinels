import sys
import janitor

sys.path.append("../")
from src import rolling


def test_p_quantile(
    var_dep="co2",
    var_idep="ta",
    n_days=7,
    date_event="2008-08-23",
    path_in="../../Data/Euroflux/BELon.csv",
):
    dep_cols = ["co2", "fc", "le", "h", "co"]
    indep_cols = ["ws", "p", "pa", "rh", "ppfd_in", "ta", "netrad"]

    # var_dep = ""
    # var_idep = ""
    varpair = (var_dep, var_idep)

    # breakpoint()
    # import glob
    # glob.glob("../../../*")
    dt, dt_select = rolling.preprocess_dt(path_in, dep_cols, indep_cols)
    dt = janitor.remove_empty(dt)
    dt_event = rolling.define_period(dt_select, n_days=n_days, date_event=date_event)
    window_size = dt_event.shape[0]

    _, _, _, _, _, _, _ = rolling.p_quantile(
        dt, dt_event, varpair[0], varpair[1], window_size
    )
