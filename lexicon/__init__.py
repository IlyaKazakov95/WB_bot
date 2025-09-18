import pandas as pd
from pathlib import Path
from .lexicon import *

Base_Dir = Path(__file__).resolve().parent
path = Base_Dir / "Mapping.xlsx"

def read_xls():
    return pd.read_excel(path, sheet_name="Sheet1")