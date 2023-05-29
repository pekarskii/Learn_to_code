import requests
from bs4 import BeautifulSoup
import json
import re

url = "https://www.cars.com/shopping/advanced-search/"
headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1"
}

with open("data/all_categories_dict.json") as file:
    all_categories = json.load(file)

count = 0
for categroy_name, category_href in all_categories.items():
     if count <2:
        req = requests.get(url = category_href, headers = headers)
        src = req.text
        print(src)
        soup = BeautifulSoup(src, 'lxml')
        models = soup.find('div', {'id': 'mobile-models-wrapper'}).find('div', {'class': 'child-group'}).find_all('label', {'class': 'sds-label'})
        print(models)
        count+=1
