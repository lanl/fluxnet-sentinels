import sys
import pandas as pd

sys.path.append("../")
from src import utils


def test_pdf_table(headers=["A", "B"]):
    dt = pd.DataFrame({"a": 1, "b": "c"}, index=[0])
    utils.pdf_table(dt, "test", "test.pdf", headers)
