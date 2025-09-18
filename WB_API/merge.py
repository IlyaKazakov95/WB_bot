import json
from lexicon import *
import matplotlib.pyplot as plt
import seaborn as sns
from . import orders_extract
from . import stock_extract
import time
import pandas as pd

def stock_process():
    data = stock_extract()
    time.sleep(5)
    with open('stock.json', 'r', encoding="utf-8") as f:
        stocks = json.loads(f.read()) # загружаем стоки
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
    df['Москва'] = df.apply(lambda x: sum(x['warehouses'][i]['quantity'] for i in range(len(x['warehouses'])) if
                                          x['warehouses'][i]['warehouseName'] == 'Электросталь' or x['warehouses'][i][
                                              'warehouseName'] == 'Коледино' or x['warehouses'][i][
                                              'warehouseName'] == 'Белые Столбы'), axis=1)
    df['Казань + Екат'] = df.apply(lambda x: sum(x['warehouses'][i]['quantity'] for i in range(len(x['warehouses'])) if
                                                 x['warehouses'][i]['warehouseName'] == 'Казань' or x['warehouses'][i][
                                                     'warehouseName'] == 'Екатеринбург - Перспективный 12'), axis=1)
    df = df.drop('warehouses', axis=1)
    df_mapping = read_xls()  # загружаем мэппинг, в lexicon __init__ функция своя
    df_mapping['barcode'] = df_mapping.apply(lambda x: str(x['barcode']), axis=1)  # датафрейм с мэппингом
    df_orders = orders_process()
    # объединяем мэппинг, стоки и продажи
    df_full = df_mapping.merge(df[['barcode', 'Всего находится на складах', 'Возвраты в пути']], left_on='barcode',
                               right_on='barcode', how='left')
    df_orders_group = df_orders.groupby('barcode').agg(total_sales=("isCancel", "count"))
    df_total = df_full.merge(df_orders_group, left_on='barcode', right_on='barcode', how='left')
    df_total['total_sales'] = df_total['total_sales'].fillna(0)
    df_total['Всего находится на складах'] = df_total['Всего находится на складах'].fillna(0)
    df_total['Возвраты в пути'] = df_total['Возвраты в пути'].fillna(0)
    df_total = df_total.sort_values(by="total_sales", ascending=False)
    df_total.to_excel("file.xlsx", sheet_name="Sheet1", index=False)

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
    plt.title("Продажи по датам")
    plt.tight_layout()
    plt.savefig("sales_by_date.png", dpi=300)  # сохранение картинки
    return df_orders