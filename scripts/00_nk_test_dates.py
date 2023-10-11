import numpy as np
import pandas as pd

# Oct 2006, First underground test that released gases
# May 2009, Second underground test
# Feb 2013, Third underground test, gases detected in Japan
# Jan 6th, 2016 H2 test about 6-10kt underground
# Sept, 2016 H2 underground test
# Sept 2017 H2 underground test, largest of all

nktests = pd.DataFrame(
    np.array(
        [
            ["2006-10-15"],
            ["2009-05-15"],
            ["2013-02-15"],
            ["2016-01-06"],
            ["2016-09-15"],
            ["2017-09-15"],
        ]
    ),
    columns=[
        "date",
    ],
)
nktests["date"] = pd.to_datetime(nktests["date"])
nktests.to_csv("data/nktests.csv", index=False)
