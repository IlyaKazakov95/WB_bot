import json

import lexicon
from lexicon import *
import matplotlib.pyplot as plt
import seaborn as sns
from WB_API.stock_extract import stock_extract
from WB_API.orders_extract import orders_extract
import time
import pandas as pd
import datetime as dt
from pathlib import Path

def orders_process():
    data = orders_extract()
    time.sleep(10)
    with open('orders.json', 'r', encoding="utf-8") as f:
        orders = json.loads(f.read()) # загружаем продажи
    df_orders = pd.DataFrame(orders)  #датафрейми с продажами
    df_orders = df_orders[df_orders.isCancel == False]
    df_orders['date'] = pd.to_datetime(df_orders['date'])
    df_orders['date_only'] = df_orders['date'].dt.date
    df_orders_by_date = df_orders.groupby('date_only').agg(total_sales=("isCancel", "count"))
    plt.figure(figsize=(12, 6))
    sns.lineplot(
        data=df_orders_by_date,
        x='date_only',
        y='total_sales',
        marker='o'
    )
    # Настройка оси X для дат
    plt.xticks(rotation=45)
    plt.xlabel("Дата")
    plt.ylabel("Количество заказов")
    plt.tight_layout()
    img_date = dt.datetime.now().strftime("%Y%m%d%H%M%S")
    img_name = f'sales_by_date {img_date}.png'
    plt.title(f"Продажи по датам. Время формирования отчета {img_date}")
    img_path = Path(__file__).parent / img_name
    plt.savefig(img_path, dpi=300)  # сохранение картинки
    plt.close()
    return df_orders, img_path

def stock_process():

    folder = Path(__file__).parent
    # Удаляем старые Excel с шаблоном "WB_stock *.xlsx"
    for old_file in folder.glob("WB_stock *.xlsx"):
        try:
            old_file.unlink()  # удаляем файл
        except Exception as e:
            print(f"Не удалось удалить {old_file}: {e}")
    data = stock_extract()
    time.sleep(3)
    with open('stock.json', 'r', encoding="utf-8") as f:
        stocks = json.loads(f.read())
    df = pd.DataFrame(stocks)
    df['В пути до получателей'] = df.apply(lambda x: sum(
        x['warehouses'][i]['quantity'] for i in range(len(x['warehouses'])) if
        x['warehouses'][i]['warehouseName'] == 'В пути до получателей'), axis=1)
    df['Возвраты в пути'] = df.apply(lambda x: sum(
        x['warehouses'][i]['quantity'] for i in range(len(x['warehouses'])) if
        x['warehouses'][i]['warehouseName'] == 'В пути возвраты на склад WB'), axis=1)
    df['Всего находится на складах'] = df.apply(lambda x: sum(
        x['warehouses'][i]['quantity'] for i in range(len(x['warehouses'])) if
        x['warehouses'][i]['warehouseName'] == 'Всего находится на складах'), axis=1)
    df = df.drop('warehouses', axis=1)
    df_orders = orders_process()[0]
    df_mapping = read_xls()
    df_mapping['barcode'] = df_mapping.apply(lambda x: str(x['barcode']), axis=1)
    df_mapping = df_mapping[['barcode', "Наименование"]]
    df_full = df_mapping.merge(df[['barcode', 'Всего находится на складах', 'Возвраты в пути']], left_on='barcode',
                               right_on='barcode', how='left')
    df_orders_group = df_orders.groupby('barcode').agg(total_sales=("isCancel", "count")).reset_index()
    df_total = df_full.merge(df_orders_group, left_on='barcode', right_on='barcode', how='left')
    df_total['total_sales'] = df_total['total_sales'].fillna(0)
    df_total['Всего находится на складах'] = df_total['Всего находится на складах'].fillna(0)
    df_total['Возвраты в пути'] = df_total['Возвраты в пути'].fillna(0)
    df_total['stock_cover'] = df_total.apply(lambda x: x['Всего находится на складах']/x['total_sales']*90 if x['total_sales'] > 0 else x['Всего находится на складах'], axis=1)
    df_total = df_total.sort_values(by="total_sales", ascending=False)
    file_date = dt.datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f'WB_stock {file_date}.xlsx'
    file_path = Path(__file__).parent / file_name
    df_total.to_excel(file_name, sheet_name="Sheet1", index=False)
    return file_path