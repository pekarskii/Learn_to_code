import requests
from bs4 import BeautifulSoup
import json

url = "https://www.cars.com/shopping/advanced-search/"
headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1"
}


with open("data/all_categories_dict.json") as file:
    all_categories = json.load(file)

# print(all_categories)
count = 0
for categroy_name, category_href in all_categories.items():
    if count <30:
        req = requests.get(url = category_href, headers = headers)
        src = req.text
        # print(src)
        soup = BeautifulSoup(src, "lxml")
        popular_makes = soup.find('div', class_='child-group').find('div', class_='grey-category')
        print(popular_makes)
        # all_categories_popular_dict = {}
        # for item in popular_makes:
        #     # print(item['value'])
        #     item_text = item.text
        #     print(item_text)

            # item_href = "https://www.cars.com/shopping/advanced-search/?list_price_max=&list_price_min=&makes[]=" + \
            #             item['value'] + "&maximum_distance=all&mileage_max=&stock_type=all&year_max=&year_min=&zip="
            # print(f"{item_text}: {item_href}")
            # all_categories_popular_dict[item_text] = item_href
        count+=1

# req = requests.get(url = "https://www.cars.com/shopping/advanced-search/?list_price_max=&list_price_min=&makes[]=acura&maximum_distance=all&mileage_max=&stock_type=all&year_max=&year_min=&zip=", headers = headers)
# src = req.text
# print(src)