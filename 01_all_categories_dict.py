import requests
from bs4 import BeautifulSoup
import json

url = "https://www.cars.com/shopping/advanced-search/"
headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1"
}

req = requests.get(url, headers=headers)
src = req.text

soup = BeautifulSoup(src, "lxml")
popular_makes = soup.find(label = 'Popular makes').find_all('option')
all_categories_popular_dict = {}
for item in popular_makes:
    # print(item['value'])
    item_text = item.text
    item_href = "https://www.cars.com/shopping/advanced-search/?list_price_max=&list_price_min=&makes[]=" + item['value'] + "&maximum_distance=all&mileage_max=&stock_type=all&year_max=&year_min=&zip="
    # print(f"{item_text}: {item_href}")
    all_categories_popular_dict[item_text] = item_href

other_makes = soup.find(label = 'Other makes').find_all('option')
all_categories_other_dict = {}
for item in other_makes:
    # print(item['value'])
    item_text = item.text
    item_href = "https://www.cars.com/shopping/advanced-search/?list_price_max=&list_price_min=&makes[]=" + item['value'] + "&maximum_distance=all&mileage_max=&stock_type=all&year_max=&year_min=&zip="
    all_categories_other_dict[item_text] = item_href

merge = all_categories_popular_dict | all_categories_other_dict

with open("data/all_categories_dict.json", "w") as file:
    json.dump(merge, file, indent=4, ensure_ascii=False)
