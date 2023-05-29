import requests
from bs4 import BeautifulSoup
import json
import time

url = "https://www.cars.com/shopping/advanced-search/"
headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1"
}
with open("data/all_categories_dict.json") as file:
    all_categories = json.load(file)
data = []
for brand, category_href in all_categories.items():
    print('начали ждать 5 секунд')
    time.sleep(5)
    print(f'Закончили ждать 5 секунд. Извлекаем брэнд {brand}')
    req = requests.get(url = category_href, headers = headers)
    src = req.text
    soup = BeautifulSoup(src, 'lxml')
    models = []
    for model in soup.find('div', {'id': 'mobile-models-wrapper'}).find('div', {'class': 'child-group'}).find_all('label', {'class': 'sds-label'}):
        model.find('span', {'class': 'filter-count'}).decompose()
        models.append(model.text.strip())
    print(f'сформировали список с моделью {brand}')
    data.append({brand: models})

print(f'записываем в файл. Hello, World')
with open("data/models.json", "w") as file:
    json.dump(data, file, indent=4, ensure_ascii=False)