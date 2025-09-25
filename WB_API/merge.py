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
    xlsx_path = Path(__file__).parent / "wb_orders_history.xlsx"
    df_orders = pd.read_excel(xlsx_path)  #датафрейми с продажами
    df_orders = df_orders[df_orders.is_cancel == False]  # А нужно ли удалять?
    df_orders['date'] = pd.to_datetime(df_orders['date'])
    df_orders['date_only'] = df_orders['date'].dt.date
    df_orders_by_date = df_orders.groupby('date_only').agg(total_sales=("is_cancel", "count"))
    plt.figure(figsize=(12, 6))
    sns.lineplot(
        data=df_orders_by_date,
        x='date_only',
        y='total_sales',
        color='blue'
    )
    # заливка под линией
    plt.fill_between(
        df_orders_by_date.index,
        df_orders_by_date['total_sales'],
        color='blue',  # цвет заливки
        alpha=0.3  # прозрачность
    )

    # Горизонтальная пунктирная линия на y=100
    plt.axhline(
        y=100,
        color='red',
        linestyle='--',  # пунктир
        linewidth=1
    )
    # Настройка оси X для дат
    plt.xticks(rotation=45)
    plt.xlabel("")
    plt.ylabel("Количество заказов")
    plt.tight_layout()
    img_date = dt.datetime.now().strftime("%Y%m%d%H%M%S")
    img_name = f'sales_by_date {img_date}.png'
    plt.title(f"Заказы по датам. Время формирования отчета {img_date}")
    img_path = Path(__file__).parent / img_name
    plt.savefig(img_path, dpi=300)  # сохранение картинки
    plt.close()
    return df_orders, img_path

def stock_status(x):
    if x == 0 or x is None:
        return "zero stock"
    elif x < 30:
        return "low stock"
    elif x < 90:
        return "normal stock"
    else:
        return "high stock"


def stock_process():

    folder = Path(__file__).parent
    # Удаляем старые Excel с шаблоном "WB_stock *.xlsx"
    for old_file in folder.glob("WB_stock *.xlsx"):
        try:
            old_file.unlink()  # удаляем файл
        except Exception as e:
            print(f"Не удалось удалить {old_file}: {e}")
    stocks = stock_extract()
    df = pd.DataFrame(stocks)
    df['В пути до получателей'] = df.apply(lambda x: sum(
        x['warehouses'][i]['quantity'] for i in range(len(x['warehouses'])) if
        x['warehouses'][i]['warehouseName'] == 'В пути до получателей'), axis=1)
    df['Поставки + Возвраты в пути'] = df.apply(lambda x: sum(
        x['warehouses'][i]['quantity'] for i in range(len(x['warehouses'])) if
        x['warehouses'][i]['warehouseName'] == 'В пути возвраты на склад WB'), axis=1)
    df['Всего находится на складах'] = df.apply(lambda x: sum(
        x['warehouses'][i]['quantity'] for i in range(len(x['warehouses'])) if
        x['warehouses'][i]['warehouseName'] == 'Всего находится на складах'), axis=1)
    df = df.drop('warehouses', axis=1)
    df_orders = orders_process()[0]
    date_filter = dt.datetime.today() - dt.timedelta(days=90)
    df_orders = df_orders[df_orders['date']>date_filter]
    df_mapping = read_xls()
    df_mapping['barcode'] = df_mapping.apply(lambda x: str(x['barcode']), axis=1)
    df_mapping = df_mapping[['barcode', "Наименование"]]
    df_full = df_mapping.merge(df[['barcode', 'Всего находится на складах', 'Поставки + Возвраты в пути']], left_on='barcode',
                               right_on='barcode', how='left')
    df_orders_group = df_orders.groupby('barcode').agg(total_sales=("is_cancel", "count")).reset_index()
    df_orders_group['barcode'] = df_orders_group['barcode'].astype(str)
    df_full['barcode'] = df_full['barcode'].astype(str)
    df_total = df_full.merge(df_orders_group, left_on='barcode', right_on='barcode', how='left')
    df_total['total_sales'] = df_total['total_sales'].fillna(0)
    df_total['Всего находится на складах'] = df_total['Всего находится на складах'].fillna(0)
    df_total['Поставки + Возвраты в пути'] = df_total['Поставки + Возвраты в пути'].fillna(0)
    df_total['stock_cover'] = df_total.apply(lambda x: int((x['Всего находится на складах'] + x['Поставки + Возвраты в пути'])/x['total_sales']*90) if x['total_sales'] > 0 else x['Всего находится на складах'], axis=1)
    df_total['stock_status'] = df_total.apply(lambda x: stock_status(x['stock_cover']), axis=1)
    df_total = df_total.sort_values(by="total_sales", ascending=False)
    file_date = dt.datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f'WB_stock {file_date}.xlsx'
    file_path = Path(__file__).parent / file_name
    df_total.to_excel(file_path, sheet_name="Sheet1", index=False)
    return file_path

def union_sales():
    xlsx_path = Path(__file__).parent / "wb_orders_history.xlsx"
    df = pd.read_excel(xlsx_path)
    df['date'] = pd.to_datetime(df['date'])
    max_date = max(df['date'])
    orders = orders_extract()
    df_orders = pd.DataFrame(orders)  #датафрейм с продажами
    df_orders = df_orders[["gNumber", "srid", "date", "barcode", "warehouseName", "regionName", "isCancel", "finishedPrice",  "totalPrice"]]
    df_orders.columns = ['order_id', 'position_id', 'date', 'barcode', 'warehouse_name', 'region', 'is_cancel', 'finished_price', 'total_price']
    df_orders['date'] = pd.to_datetime(df_orders['date'])
    df_orders = df_orders[df_orders['date'] >= max_date]
    df = df[df['date'] < max_date]
    df_final = pd.concat([df, df_orders])
    df_final.to_excel(xlsx_path, index=False)
    return True


def wb_order_graphics_by_sku(filter=None):
    current_file = Path(__file__).resolve()
    orders_file = current_file.parent / 'wb_orders_history.xlsx'
    df = pd.read_excel(orders_file)
    df['date'] = pd.to_datetime(df['date'])
    df['date_new'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['week'] = df['date'].dt.isocalendar().week  # ISO-неделя
    df = df[df.is_cancel == False]
    df_all_weeks = df.groupby(['year', 'week']).agg(total_sales=('is_cancel', 'count')).reset_index() # создаем все недели, чтобы потом объединить
    df_all_weeks['year_week'] = df_all_weeks['year'].astype(str) + '-W' + df_all_weeks['week'].astype(str)
    if filter is not None:
        df = df[df['barcode']==int(filter)]
    df_grouped_week = df.groupby(['year', 'week', 'barcode']).agg(total_sales=('is_cancel', 'count')).reset_index()
    df_grouped_week['year_week'] = df_grouped_week['year'].astype(str) + '-W' + df_grouped_week['week'].astype(str)
    df_all_weeks = df_all_weeks[['year_week']].merge(df_grouped_week[['year_week','total_sales', 'barcode']], left_on = "year_week", right_on = "year_week", how='left')
    df_mapping = read_xls()
    df_mapping = df_mapping[['barcode', "Наименование"]]
    df_all_weeks = df_all_weeks.merge(df_mapping, left_on='barcode',
                               right_on='barcode', how='left')
    plt.figure(figsize=(12, 6))
    if filter is not None:
        filter_name = f"Заказы по {df_all_weeks['Наименование'].iloc[0]}"
    else:
        filter_name = "Заказы по датам"
    sns.barplot(
        data=df_all_weeks,
        x='year_week',
        y='total_sales',
        width=0.5,
        facecolor='lightgreen',
        alpha=0.6,
        edgecolor='black',
        linewidth=1
    )
    # Разрежение меток по оси X
    step = 2  # показывать каждую 5-ю дату
    plt.xticks(
        ticks=range(0, len(df_all_weeks), step),
        labels=df_all_weeks['year_week'][::step],
        rotation=70,
        fontsize=9
    )
    plt.xlabel("")
    plt.ylabel(f"Заказано, штук")
    plt.title(filter_name)
    plt.tight_layout()
    timestamp = dt.datetime.now().strftime("%Y%m%d%H%M%S")
    if filter:
        img_name = f"wb_sales_sku_{filter}_{timestamp}.png"
    else:
        img_name = f"wb_sales_all_{timestamp}.png"
    img_path = Path(__file__).parent / img_name
    plt.savefig(img_path, dpi=300)
    plt.close()
    return img_path



def wb_ozon_order_graphics_by_sku(filter=None):
    # блок WB
    current_file = Path(__file__).resolve()
    orders_file = current_file.parent / 'wb_orders_history.xlsx'
    df = pd.read_excel(orders_file)
    df['date'] = pd.to_datetime(df['date'])
    df['date_new'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['week'] = df['date'].dt.isocalendar().week  # ISO-неделя
    df = df[df.is_cancel == False]
    df_all_weeks = df.groupby(['year', 'week']).agg(total_sales=('is_cancel', 'count')).reset_index() # создаем все недели, чтобы потом объединить
    df_all_weeks['year_week'] = df_all_weeks['year'].astype(str) + '-W' + df_all_weeks['week'].astype(str)
    if filter is not None:
        df = df[df['barcode']==int(filter)]
    df_grouped_week = df.groupby(['year', 'week', 'barcode']).agg(total_sales=('is_cancel', 'count')).reset_index()
    df_grouped_week['year_week'] = df_grouped_week['year'].astype(str) + '-W' + df_grouped_week['week'].astype(str)
    df_all_weeks = df_all_weeks[['year_week']].merge(df_grouped_week[['year_week','total_sales', 'barcode']], left_on = "year_week", right_on = "year_week", how='left')
    df_mapping = read_xls()
    df_mapping = df_mapping[['barcode', 'Наименование', 'Ozon_SKU']]
    df_all_weeks = df_all_weeks.merge(df_mapping, left_on='barcode',
                               right_on='barcode', how='left')
    df_all_weeks["site"] = "Wildberries"
    # блок Озона
    orders_file = current_file.parent / 'ozon_orders.xlsx'
    df = pd.read_excel(orders_file)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['date'] = df['created_at'].dt.date
    df['year'] = df['created_at'].dt.year
    df['week'] = df['created_at'].dt.isocalendar().week  # ISO-неделя
    df_all_weeks2 = df.groupby(['year', 'week']).agg(total_sales=('quantity', 'sum')).reset_index() # создаем все недели, чтобы потом объединить
    df_all_weeks2['year_week'] = df_all_weeks2['year'].astype(str) + '-W' + df_all_weeks2['week'].astype(str)
    if filter is not None:
        filter2 = df_mapping[df_mapping['barcode']==int(filter)]['Ozon_SKU'].iloc[0]
        df = df[df['sku']==int(filter2)]
    df_grouped_week = df.groupby(['year', 'week']).agg(total_sales=('quantity', 'sum')).reset_index()
    df_grouped_week['year_week'] = df_grouped_week['year'].astype(str) + '-W' + df_grouped_week['week'].astype(str)
    df_all_weeks2 = df_all_weeks2[['year_week']].merge(df_grouped_week[['year_week','total_sales']], left_on = "year_week", right_on = "year_week", how='left')
    df_all_weeks2["barcode"] = int(filter)
    df_all_weeks2["Наименование"] = df_mapping[df_mapping['barcode']==int(filter)]['Наименование'].iloc[0]
    df_all_weeks2["Ozon_SKU"] = df_mapping[df_mapping['barcode']==int(filter)]['Ozon_SKU'].iloc[0]
    df_all_weeks2["site"] = "Ozon"
    df_total = pd.concat([df_all_weeks, df_all_weeks2])
    # строим накопленную диаграмму
    custom_palette = {
        "Wildberries": "purple",
        "Ozon": "blue",
    }
    plt.figure(figsize=(12, 6))
    sns.histplot(
        data=df_total,
        x="year_week",
        weights="total_sales",
        hue="site",
        multiple="stack",
        shrink=0.8,
        alpha=0.6,
        palette=custom_palette,
        edgecolor="black", # чёрный контур
        linewidth=1.1
    )
    weeks = df_total['year_week'].unique()
    # Разрежение меток по оси X
    step = 5  # показывать каждую 5-ю дату
    plt.xticks(
        ticks=range(0, len(weeks), step),
        labels=weeks[::step],
        rotation=60,
        fontsize=9
    )
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xlabel("")
    plt.ylabel("Заказано, штук")
    timestamp = dt.datetime.now().strftime("%Y%m%d%H%M%S")
    if filter:
        filter_name = df_mapping[df_mapping['barcode']==int(filter)]['Наименование'].iloc[0]
        plt.title(filter_name)
        img_name = f"wb_and_ozon_sales_sku_{filter}_{timestamp}.png"
    else:
        plt.title("Заказы WB + Ozon")
        img_name = f"wb_and_ozon_sales_all_{timestamp}.png"
    img_path = Path(__file__).parent / img_name
    plt.savefig(img_path, dpi=300)
    plt.close()
    return img_path
