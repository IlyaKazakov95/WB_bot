import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import datetime as dt
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots

def ozon_order_graphics():
    df = pd.read_excel('ozon_orders.xlsx')
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['date'] = df['created_at'].dt.date
    df_grouped = df.groupby(['date']).agg(total_sales=("quantity", "sum")).reset_index()
    df_grouped['date'] = pd.to_datetime(df_grouped['date'])
    plt.figure(figsize=(12, 6))
    sns.barplot(
        data=df_grouped,
        x='date',
        y='total_sales',
        width=0.5
    )
    # Разрежение меток по оси X
    step = 20  # показывать каждую 5-ю дату
    plt.xticks(
        ticks=range(0, len(df_grouped), step),
        labels=df_grouped['date'].dt.strftime('%Y-%m-%d')[::step],
        rotation=70,
        fontsize=9
    )
    plt.xlabel("")
    plt.ylabel("Заказано, штук")
    plt.title("Продажи по датам")
    plt.tight_layout()
    plt.savefig("ozon_sales_by_date.png", dpi=600)


def ozon_order_graphics_by_sku(filter=None):
    df = pd.read_excel('ozon_orders.xlsx')
    if filter is not None:
        df = df[df['sku']==filter]
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['date'] = df['created_at'].dt.date
    df['year'] = df['created_at'].dt.year
    df['week'] = df['created_at'].dt.isocalendar().week  # ISO-неделя
    df_grouped_week = df.groupby(['year', 'week', 'name']).agg(total_sales=('quantity', 'sum')).reset_index()
    df_grouped_week['year_week'] = df_grouped_week['year'].astype(str) + '-W' + df_grouped_week['week'].astype(str)
    plt.figure(figsize=(12, 6))
    if filter is not None:
        filter_name = f"Продажи по {df_grouped_week['name'].iloc[0]}"
    else:
        filter_name = "Продажи по датам"
    sns.barplot(
        data=df_grouped_week,
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
        ticks=range(0, len(df_grouped_week), step),
        labels=df_grouped_week['year_week'][::step],
        rotation=70,
        fontsize=9
    )
    plt.xlabel("")
    plt.ylabel(f"Заказано, штук")
    plt.title(filter_name)
    plt.tight_layout()
    plt.savefig("ozon_sales_by_week_sku.png", dpi=600)


# # df_grouped содержит 'date' и 'total_sales'
# df_grouped['date'] = pd.to_datetime(df_grouped['date'])
# df_grouped['year_month'] = df_grouped['date'].dt.strftime('%Y_%m')
#
# # Сумма продаж по месяцам
# monthly_sales = df_grouped.groupby('year_month')['total_sales'].sum().reset_index()
#
# # Создаём фигуру с графиком и таблицей
# fig = make_subplots(
#     rows=2, cols=1,
#     row_heights=[0.7, 0.3],
#     specs=[[{"type": "xy"}],
#            [{"type": "table"}]]
# )
#
# # Добавляем график продаж
# fig.add_trace(go.Scatter(
#     x=df_grouped['date'],
#     y=df_grouped['total_sales'],
#     mode='lines',
#     name='Продажи',
#     line=dict(color='royalblue', width=2),
#     fill='tozeroy',
#     hovertemplate='Дата: %{x}<br>Продажи: %{y}<extra></extra>'
# ), row=1, col=1)
#
# # Линия тренда
# z = np.polyfit(pd.to_numeric(df_grouped['date']), df_grouped['total_sales'], 1)
# p = np.poly1d(z)
# df_grouped['trend'] = p(pd.to_numeric(df_grouped['date']))
# fig.add_trace(go.Scatter(
#     x=df_grouped['date'],
#     y=df_grouped['trend'],
#     mode='lines',
#     name='Линия тренда',
#     line=dict(color='firebrick', width=2, dash='dash'),
#     hoverinfo='skip'
# ), row=1, col=1)
#
# # Таблица под графиком (одна строка, колонки - месяц, значения - продажи)
# fig.add_trace(go.Table(
#     header=dict(values=monthly_sales['year_month'], fill_color='lightgrey'),
#     cells=dict(values=[monthly_sales['total_sales']], fill_color='white')
# ), row=2, col=1)
#
# # Оформление фигуры
# fig.update_layout(
#     title=dict(text='Продажи по датам и по месяцам', x=0.5),
#     height=900,
#     width=1800,
#     plot_bgcolor='white',
#     paper_bgcolor='white'
# )
#
# # Сохраняем интерактивный HTML
# fig.write_html("ozon_sales_with_table.html")
#
# fig.show()