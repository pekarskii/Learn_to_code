import requests
from bs4 import BeautifulSoup
import json
import time
import pyarrow as pa
import pyarrow.parquet as pq

url = "https://www.cars.com/shopping/advanced-search/"
headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1"
}

with open("data/all_categories_dict.json") as file:
    all_categories = json.load(file)
count=0
data = []
for brand, category_href in all_categories.items():
    time.sleep(2)
    req = requests.get(url = category_href, headers = headers)
    src = req.text
    soup = BeautifulSoup(src, 'lxml')
    models = []
    for model in soup.find('div', {'id': 'mobile-models-wrapper'}).find('div', {'class': 'child-group'}).find_all('label', {'class': 'sds-label'}):
        model.find('span', {'class': 'filter-count'}).decompose()
        models.append(model.text.strip())
    data.append({"brand":brand,"models":models})
    print(f'{len(all_categories) - count}/{len(all_categories)}.{brand}({len(models)})шт.')
    count+=1
    print(f'"brand:"{brand}","model":"{models}"')



print(f'Записываем данные в файл.')
table = pa.Table.from_pydict({key: [dic[key] for dic in data] for key in data[0]})
pq.write_table(table, 'data/data.parquet')



# with jsonlines.open('data/all_brands_models_dict.jsonl', mode='w') as writer:
#     for obj in data:
#         writer.write(obj)