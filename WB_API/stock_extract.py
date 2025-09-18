import requests
import json
from environs import Env
import time
url = 'https://seller-analytics-api.wildberries.ru/api/v1/warehouse_remains'

def stock_extract():
    env = Env()
    env.read_env()
    response = requests.get(url, headers = {"Authorization": env('HeaderApiToken')}, params = {"groupByBarcode": True}, verify=True)
    task_id = response.json()['data']['taskId']
    time.sleep(2) # делаем задержку, чтобы task_id успел сформироваться
    # надо прописать обработку исключений здесь, если task_id не будет
    getting_report = f'https://seller-analytics-api.wildberries.ru/api/v1/warehouse_remains/tasks/{task_id}/download'
    response = requests.get(getting_report, headers = {"Authorization": env('HeaderApiToken')}, verify=True)
    response = response.json()
    with open('stock.json', 'w', encoding="utf-8") as f:
        f.write(json.dumps(response, ensure_ascii=False, indent=4))