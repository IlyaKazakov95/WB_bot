import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import datetime as dt
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots
from pathlib import Path
import matplotlib.dates as mdates

def ozon_order_graphics():
    current_file = Path(__file__).resolve()
    orders_file = current_file.parent / 'ozon_orders.xlsx'
    df = pd.read_excel(orders_file)
    df['created_at'] = pd.to_datetime(df['created_at'])

    # Оставляем Timestamp вместо datetime.date
    df['date'] = df['created_at'].dt.normalize()

    df_grouped = df.groupby('date').agg(total_sales=("quantity", "sum")).reset_index()

    plt.figure(figsize=(12, 6))
    sns.lineplot(
        data=df_grouped,
        x='date',
        y='total_sales',
        color='blue'
    )
    # заливка под линией
    plt.fill_between(
        df_grouped['date'],
        df_grouped['total_sales'],
        color='blue',  # цвет заливки
        alpha=0.3  # прозрачность
    )
    # ===== Среднее значение =====
    mean_val = df_grouped['total_sales'].mean()
    plt.axhline(mean_val, color="red", linestyle="--", linewidth=1.5, label=f"Среднее: {mean_val:.1f}")

    # ===== Линия тренда =====
    x = np.arange(len(df_grouped))
    y = df_grouped['total_sales'].values
    if len(x) > 1:  # тренд только если есть больше одной точки
        coef = np.polyfit(x, y, 1)  # линейная регрессия (степень 1)
        trend = np.polyval(coef, x)
        plt.plot(df_grouped['date'], trend, color='blue', linestyle='--', linewidth=2, label="Тренд")

    plt.legend(
        loc="upper right",       # где разместить (можно 'upper left', 'lower right' и т.д.)
        frameon=True,            # включаем рамку
        fancybox=True,           # скруглённые углы
        shadow=True,             # тень под рамкой
        fontsize=10
    )

    # Настройка оси X для дат
    plt.xticks(rotation=45)
    plt.xlabel("")
    plt.ylabel("Заказано, штук")
    plt.title("Заказы по датам")
    plt.tight_layout()
    timestamp = dt.datetime.now().strftime("%Y%m%d%H%M%S")
    img_name = f'ozon_sales_by_date {timestamp}.png'
    img_path = Path(__file__).parent / img_name
    plt.savefig(img_path, dpi=300)
    plt.close()
    return img_path


def ozon_order_graphics_by_sku(filter=None):
    current_file = Path(__file__).resolve()
    orders_file = current_file.parent / 'ozon_orders.xlsx'
    df = pd.read_excel(orders_file)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['date'] = df['created_at'].dt.date
    df['year'] = df['created_at'].dt.year
    df['week'] = df['created_at'].dt.isocalendar().week  # ISO-неделя
    df_all_weeks = df.groupby(['year', 'week']).agg(total_sales=('quantity', 'sum')).reset_index() # создаем все недели, чтобы потом объединить
    df_all_weeks['year_week'] = df_all_weeks['year'].astype(str) + '-W' + df_all_weeks['week'].astype(str)
    if filter is not None:
        df = df[df['sku']==int(filter)]
    df_grouped_week = df.groupby(['year', 'week', 'name']).agg(total_sales=('quantity', 'sum')).reset_index()
    df_grouped_week['year_week'] = df_grouped_week['year'].astype(str) + '-W' + df_grouped_week['week'].astype(str)
    df_all_weeks = df_all_weeks[['year_week']].merge(df_grouped_week[['year_week','total_sales', 'name']], left_on = "year_week", right_on = "year_week", how='left')
    plt.figure(figsize=(12, 6))
    if filter is not None:
        filter_name = f"Заказы по {df_all_weeks['name'].dropna().iloc[0]}"
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
    # ===== Среднее значение =====
    mean_val = df_all_weeks['total_sales'].mean()
    plt.axhline(mean_val, color="red", linestyle="--", linewidth=1.5, label=f"Среднее: {mean_val:.1f}")

    # ===== Линия тренда =====
    x = np.arange(len(df_all_weeks))
    y = df_all_weeks['total_sales'].fillna(0).values
    if len(x) > 1:  # тренд только если есть больше одной точки
        coef = np.polyfit(x, y, 1)  # линейная регрессия (степень 1)
        trend = np.polyval(coef, x)
        plt.plot(df_all_weeks['year_week'], trend, color='blue', linestyle='--', linewidth=2, label="Тренд")

    plt.legend(
        loc="upper right",       # где разместить (можно 'upper left', 'lower right' и т.д.)
        frameon=True,            # включаем рамку
        fancybox=True,           # скруглённые углы
        shadow=True,             # тень под рамкой
        fontsize=10
    )
    plt.xlabel("")
    plt.ylabel(f"Заказано, штук")
    plt.title(filter_name)
    plt.tight_layout()
    timestamp = dt.datetime.now().strftime("%Y%m%d%H%M%S")
    if filter:
        img_name = f"ozon_sales_sku_{filter}_{timestamp}.png"
    else:
        img_name = f"ozon_sales_all_{timestamp}.png"
    img_path = Path(__file__).parent / img_name
    plt.savefig(img_path, dpi=300)
    plt.close()
    return img_path


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

def ozon_order_graphics_3_month():
    current_file = Path(__file__).resolve()
    orders_file = current_file.parent / 'ozon_orders.xlsx'
    df = pd.read_excel(orders_file)
    df['created_at'] = pd.to_datetime(df['created_at'], utc=True)
    date_filter = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=90)  # UTC для совпадения с колонкой
    df = df[df['created_at']>date_filter]
    df['date'] = df['created_at'].dt.date
    df_grouped = df.groupby('date').agg(total_sales=("quantity", "sum")).reset_index()

    plt.figure(figsize=(12, 6))
    sns.lineplot(
        data=df_grouped,
        x='date',
        y='total_sales',
        color='blue'
    )
    # заливка под линией
    plt.fill_between(
        df_grouped['date'],
        df_grouped['total_sales'],
        color='blue',  # цвет заливки
        alpha=0.3  # прозрачность
    )

    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.xticks(rotation=70)
    # yesterday и today
    today = dt.date.today()
    yesterday = today - dt.timedelta(days=1)
    # получаем значение за вчера
    yest_value = df_grouped.loc[df_grouped["date"] == yesterday, "total_sales"]
    if not yest_value.empty:
        yest_value = yest_value.values[0]
    else:
        yest_value = None
    # горизонтальная пунктирная линия по вчерашнему значению
    if yest_value is not None:
        plt.axhline(y=yest_value, color="black", linestyle="--", alpha=0.6)
        plt.scatter(df_grouped.loc[df_grouped["date"] == yesterday, "date"], yest_value,
                    color="black", zorder=5, s=80, label=f"Вчера: {yest_value:.1f}")
    # зеленая точка на сегодняшней дате
    today_value = df_grouped.loc[df_grouped["date"] == today, "total_sales"]
    if not today_value.empty:
        plt.scatter(df_grouped.loc[df_grouped["date"] == today, "date"], today_value,
                    color="green", zorder=5, s=80, label=f"Сегодня: {today_value.values[0]:.1f}")
    # ===== Среднее значение =====
    mean_val = df_grouped['total_sales'].mean()
    plt.axhline(mean_val, color="red", linestyle="--", linewidth=1.5, label=f"Среднее: {mean_val:.1f}")

    # ===== Линия тренда =====
    x = np.arange(len(df_grouped))
    y = df_grouped['total_sales'].values
    if len(x) > 1:  # тренд только если есть больше одной точки
        coef = np.polyfit(x, y, 1)  # линейная регрессия (степень 1)
        trend = np.polyval(coef, x)
        plt.plot(df_grouped['date'], trend, color='blue', linestyle='--', linewidth=2, label="Тренд")

    plt.legend(
        loc="upper right",       # где разместить (можно 'upper left', 'lower right' и т.д.)
        frameon=True,            # включаем рамку
        fancybox=True,           # скруглённые углы
        shadow=True,             # тень под рамкой
        fontsize=10
    )

    # Настройка оси X для дат
    plt.xticks(rotation=45)
    plt.xlabel("")
    plt.ylabel("Заказано, штук")
    plt.title("Заказы по датам")
    plt.tight_layout()
    timestamp = dt.datetime.now().strftime("%Y%m%d%H%M%S")
    img_name = f'ozon_sales_by_date_3_month {timestamp}.png'
    img_path = Path(__file__).parent / img_name
    plt.savefig(img_path, dpi=300)
    plt.close()
    return img_path

def ozon_stock_dynamic():
    xlsx_path = Path(__file__).parent / "ozon_stock_history.xlsx"
    df = pd.read_excel(xlsx_path)
    df_group = df.groupby(['date'], as_index=False).agg(stock=('stock', 'sum'))
    df_group['date'] = pd.to_datetime(df_group['date'])
    plt.figure(figsize=(12, 6))
    sns.lineplot(
        data=df_group,
        x='date',
        y='stock',
        color='red'
    )
    # заливка под линией
    plt.fill_between(
        df_group['date'],
        df_group['stock'],
        color='red',  # цвет заливки
        alpha=0.3  # прозрачность
    )
    # ===== Среднее значение =====
    mean_val = df_group['stock'].mean()
    plt.axhline(mean_val, color="blue", linestyle="--", linewidth=1.5, label=f"Средний сток: {mean_val:.1f}")
    # получаем значение за последний день
    date_filter = max(df_group['date'])
    date_value = df_group.loc[df_group["date"] == date_filter, "stock"]
    if not date_value.empty:
        date_value = date_value.values[0]
    else:
        date_value = None
    # горизонтальная пунктирная линия по последнему значению стока
    if date_value is not None:
        plt.axhline(y=date_value, color="black", linestyle="--", alpha=0.6)
        plt.scatter(df_group.loc[df_group["date"] == date_filter, "date"], date_value,
                    color="black", zorder=5, s=80, label=f"Текущий сток: {date_value:.1f}")

    # Настройка оси X для дат
    plt.xlabel("")
    plt.ylabel("Уровень товарных запасов Озон")
    plt.legend()
    img_date = dt.datetime.now().strftime("%Y%m%d%H%M%S")
    img_name = f'ozon_stock_history {img_date}.png'
    plt.title(f"Динамика стока Озон. Время формирования отчета {img_date}")
    plt.tight_layout()
    img_path = Path(__file__).parent / img_name
    plt.savefig(img_path, dpi=300)  # сохранение картинки
    plt.close()
    return img_path