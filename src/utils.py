import re
import pandas as pd


def amf_clean(dt_raw):
    """
    import janitor
    file_in = "../../Data/Asiaflux\\FxMt_FHK_2010_30m_02\\FxMt_FHK_2010_30m_02.csv"
    names = pd.read_csv(file_in, nrows=1, encoding="Shift_JIS").clean_names()
    dt = pd.read_csv(
        file_in,
        skiprows=1,
        encoding="Shift_JIS",
        na_values=["-9999.0"],
    )
    dt.columns = [x for x in names.columns]
    dt_raw = janitor.remove_empty(dt)
    """
    old_names = [x for x in dt_raw.columns]
    new_names = [re.sub("_\\d{1,3}_\\d{1,3}_\\d{1,2}", "", x) for x in old_names]
    new_names = [re.sub("_\\d{1,3}", "", x) for x in new_names]
    new_names = [re.sub("\\.\\d{1,3}", "", x) for x in new_names]
    dt = dt_raw.copy()
    dt.columns = new_names

    # remove duplicate columns sorted by least number of missing values
    n_not_missing = [sum(~pd.isna(dt.iloc[:, i])) for i in range(dt.shape[1])]
    rank_not_missing = [
        x for x, _ in sorted(enumerate(n_not_missing), key=lambda x: x[1])
    ]
    rank_not_missing.reverse()
    dt = dt.iloc[:, rank_not_missing].copy()
    dt = dt.loc[:,~dt.columns.duplicated()].copy()

    return dt
