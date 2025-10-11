import pandas as pd
from pathlib import Path
from .lexicon import *

Base_Dir = Path(__file__).resolve().parent
path = Base_Dir / "Mapping.xlsx"

def read_xls():
    return pd.read_excel(path, sheet_name="Sheet1")

wb_arrivals = Base_Dir / 'WB_arrivals.xlsx'

def read_arrivals():
    return pd.read_excel(wb_arrivals, sheet_name='Sheet1')

wb_whs = Base_Dir / 'WB_warehouses.xlsx'
def read_whs():
    return pd.read_excel(wb_whs, sheet_name='Sheet1')