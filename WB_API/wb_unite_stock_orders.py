import pandas as pd
from lexicon import *
from WB_API.merge import orders_process
import datetime as dt
from pathlib import Path

def wb_stock_orders_unite():
    file_path = Path(__file__).parent / 'wb_stock_history.xlsx'
    df = pd.read_excel(file_path)
    whs = read_whs()
    clusters = pd.DataFrame(whs['Кластер'].drop_duplicates())
    clusters = clusters.rename(columns={'Кластер': 'cluster'})
    df = df[['date', 'warehouse', 'barcode', 'giId', 'barcodesCount']]
    df = df.merge(whs, left_on='warehouse', right_on='Основные склады', how='left')
    df = df.drop(['warehouse', 'Основные склады'], axis=1)
    df = df.rename(columns={'Кластер': 'cluster'})
    df = df[df['barcodesCount'] > 0]
    df_mapping = read_xls()
    df_orders = orders_process()[0]
    df_orders['date'] = pd.to_datetime(df_orders['date'])
    df_orders = df_orders[df_orders['date'].dt.date>=dt.date(2024,1,1)]
    df_orders['date'] = df_orders['date'].dt.date
    df_orders_date = pd.DataFrame(df_orders['date'].drop_duplicates())
    df_full = df_orders_date.merge(df_mapping, how="cross")
    df_full = df_full.merge(clusters, how="cross")
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df = df.groupby(['date', 'barcode', 'cluster']).agg(stock_qty=('barcodesCount', 'sum')).reset_index()
    df_full = df_full.merge(df, how="left", left_on=['date', 'barcode', 'cluster'], right_on=['date', 'barcode','cluster'])
    df_orders = df_orders[df_orders.is_cancel == False]
    df_orders = df_orders.merge(whs, left_on='warehouse_name', right_on='Основные склады', how='left')
    df_orders = df_orders.rename(columns={'Кластер': 'cluster'})
    df_orders = df_orders.groupby(['date', 'barcode', 'cluster']).agg(total_sales=("is_cancel", "count")).reset_index()
    df_full = df_full.merge(df_orders, how="left", left_on=['date', 'barcode', 'cluster'], right_on=['date', 'barcode', 'cluster'])
    df_full['total_sales'] = df_full['total_sales'].fillna(0)
    df_full['stock_qty'] = df_full['stock_qty'].fillna(0)
    df_full_agg = df_full[(df_full['total_sales']>0) | (df_full['stock_qty']>0)].groupby('barcode').agg(min_date=('date', 'min')).reset_index()
    df_full = df_full.merge(df_full_agg, how="left", left_on='barcode', right_on='barcode')
    df_full['filter'] = df_full.apply(lambda x: 1 if x['date'] >= x['min_date'] else 0, axis=1)
    df_full = df_full[df_full['filter']==1]
    df_full['OOS'] = df_full.apply(lambda x: 1 if x['stock_qty'] == 0 else 0, axis=1)
    df_full_agg_new = df_full[(df_full['total_sales']>0) | (df_full['stock_qty']>0)].groupby('barcode').agg(max_date=('date', 'max')).reset_index()
    df_full = df_full.merge(df_full_agg_new, how="left", left_on='barcode', right_on='barcode')
    df_full['days_wo_sales_stock'] = df_full.apply(lambda x: (dt.date.today() - x['max_date']).days, axis=1)
    df_forecast = df_full[['date', 'barcode', 'total_sales', 'OOS']]
    df_forecast = df_forecast.copy()
    df_forecast['date'] = pd.to_datetime(df_forecast['date'])
    df_forecast['month'] = df_forecast['date'].dt.month
    df_forecast['day_of_week'] = df_forecast['date'].dt.dayofweek
    new_file_path = Path(__file__).parent / 'wb_stock_orders.xlsx'
    df_full.to_excel(new_file_path, sheet_name='Sheet1', index=False)
    return new_file_path
