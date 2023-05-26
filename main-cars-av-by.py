from bs4 import BeautifulSoup
import requests
import csv
import time
import json
import os


start_time = time.time()
start_time_str = time.strftime('%Y-%m-%d-%H-%M-%S', time.gmtime(start_time))

DEFAULT_HEADER = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

SITE_URL = "https://cars.av.by"

CSV_CARD_FILENAME_AV_BY = f"scrapped_data/AV_BY/CSV/{start_time_str}/cars-av-by_card.csv"
CSV_CARD_GALLERY_FILENAME_AV_BY = f"scrapped_data/AV_BY/CSV/{start_time_str}/cars-av-by_card_gallery.csv"
CSV_CARD_OPTIONS_FILENAME_AV_BY = f"scrapped_data/AV_BY/CSV/{start_time_str}/cars-av-by_card_options.csv"
CSV_CARD_URL_AV_BY = f"scrapped_data/AV_BY/CSV/{start_time_str}/cars-av-by_card_url.csv"
LOG_FILENAME_AV_BY = f"./logs/AV_BY/{start_time_str}/cars-av-by_log.txt"

def get_info_from_next_data(text):
    next_data = json.loads(text)

    advert = next_data["props"]["initialState"]["advert"]["advert"].copy()

    advert_id = advert["id"]
    publicUrl = advert["publicUrl"]

    photos =  {}
    photos["id"] = advert_id
    photos["publicUrl"] = publicUrl
    photos["photos"] = advert["photos"].copy()

    properties = {}
    properties["id"] = advert_id
    properties["publicUrl"] = publicUrl
    properties["properties"] = advert["properties"].copy()

    similarAdverts = [{"id": ad["id"], "publicUrl": ad["publicUrl"]} for ad in next_data["props"]["initialState"]["advert"]["similarAdverts"]]

    return advert, photos, properties, similarAdverts


def get_parsed_card(url, debug=0, headers=DEFAULT_HEADER):
    card_dict = {}

    page = requests.get(url, headers=headers)
    # if debug:
    #     print(page.status_code,"\n")

    if page.status_code == 200:
        soup = BeautifulSoup(page.text, "html.parser")

        card = soup.find("div", class_="card")
        # print(card,"\n")

        card_gallery = card.find("div", class_="gallery__stage-shaft")
        card_dict["gallery"] = []
        # if debug:
        #     print("Галлерея")
        try:
            for div_img in card_gallery.find_all("div", class_="gallery__frame"):
                img = div_img.find("img")
                # if debug:
                #     print(img["data-srcset"])
                card_dict["gallery"].append(img["data-srcset"].split()[0])
        except:
            pass

        card_title = card.find(class_="card__title")
        # if debug:
        #     print(f"card_title: {card_title.text}")
        card_dict["title"] = card_title.text

        card_price_primary = card.find(class_="card__price-primary")
        # if debug:
        #     print(f"card_price_primary: {card_price_primary.text}")
        card_dict["price_primary"] = card_price_primary.text

        card_price_secondary = card.find(class_="card__price-secondary")
        # if debug:
        #     print(f"card__price-secondary: {card_price_secondary.text}")
        card_dict["price_secondary"] = card_price_secondary.text

        card_comment = card.find("div", class_="card__comment-text")
        # if debug:
        #     print(f"card_comment: {card_comment.text}")
        try:
            card_dict["comment"] = card_comment.get_text(separator="|", strip=True).replace("\n", "|")
        except:
            card_dict["comment"] = ""

        card_location = card.find("div", class_="card__location")
        try:
            card_dict["location"] = card_location.text
        except:
            card_dict["location"] = ""

        labels = []
        card_labels = card.find("div", class_="card__labels")
        try:
            for div in card_labels.find_all("div"):
                if div.has_attr('class') and len(div['class']) > 1 and div['class'][1] in ["badge--top", "badge--parts", "badge--wreck", "badge--vin"]:
                    if  div['class'][1] == "badge--top":
                        labels += ["Top"]
                    else:
                        labels += [div.text]
        except:
            pass
        card_dict["labels"] = "|".join(labels)

        card_params = card.find("div", class_="card__params")
        card_description = card.find("div", class_="card__description")
        # if debug:
        #     print(f"card_description: {card_params.text}\n{card_description.text}")
        card_dict["description"] = card_params.text + " | " + card_description.text

        card_exchange = card.find(class_="card__exchange-title")
        # if debug:
        #     print(f"card_exchange: {card_exchange.text}")
        card_dict["exchange"] = card_exchange.text

        card_dict["scrap_date"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

        card_options = card.find(class_="card__options-wrap")
        card_dict["options"] = []
        # print(card_options)

        for section in card_options.find_all("div", class_="card__options-section"):
            # print(section)
            section_dict = {}

            category = section.find(class_="card__options-category")
            # if debug:
            #     print(f"category: {category.text}")
            section_dict["category"] = category.text

            section_dict["items"] = []
            for option in section.find_all(class_="card__options-item"):
                # if debug:
                #     print(f"   - {option.text}")
                section_dict["items"].append(option.text)

            card_dict["options"].append(section_dict)

        card_dict["json"] = {}
        try:
            next_data = soup.find("script", id="__NEXT_DATA__")
            advert, photos, properties, similarAdverts = get_info_from_next_data(next_data.text)

            card_dict["json"]["advert"] = advert
            card_dict["json"]["photos"] = photos
            card_dict["json"]["properties"] = properties
            card_dict["json"]["similarAdverts"] = similarAdverts
        except:
            pass

        # if debug:
        #     print("\n",str(card_dict).replace("\\xa0", " ").replace("\\u2009", " "))

    return card_dict


# print(get_parsed_card(url))

def get_card_url_list(url, site_url=SITE_URL, headers=DEFAULT_HEADER):
    url_list = []

    page = requests.get(url, headers=headers)
    if page.status_code == 200:
        soup = BeautifulSoup(page.text, "html.parser")

        listing_items = soup.find_all("div", class_="listing-item")
        try:
            for item in listing_items:
                item_href = item.find("a", class_="listing-item__link")["href"]
                url_list.append(site_url+item_href)
        except:
            pass

    return url_list


def make_folder(start_folder, subfolders_chain):
    folder = start_folder
    for subfolder in subfolders_chain:
        folder += "/" + subfolder
        if not os.path.isdir(folder):
            os.mkdir(folder)

    return folder

def main():
    make_folder(f"{os.curdir}", ["scrapped_data", "AV_BY", "JSON", start_time_str])
    make_folder(f"{os.curdir}", ["scrapped_data", "AV_BY", "CSV", start_time_str])
    make_folder(f"{os.curdir}", ["logs", "AV_BY", start_time_str])

    with \
        open(LOG_FILENAME_AV_BY, 'w', newline="", encoding="utf-8") as log_file, \
        open(CSV_CARD_FILENAME_AV_BY, 'a', newline="", encoding="utf-8") as card_csvfile, \
        open(CSV_CARD_GALLERY_FILENAME_AV_BY, 'a', newline="", encoding="utf-8") as card_gallery_csvfile, \
        open(CSV_CARD_OPTIONS_FILENAME_AV_BY, 'a', newline="", encoding="utf-8") as card_options_csvfile, \
        open(CSV_CARD_URL_AV_BY, 'a', newline="", encoding="utf-8") as card_url_csvfile:

        print(f"start time (GMT): {time.strftime('%X', time.gmtime())}", file=log_file)

        card_fieldnames = "card_id,title,price_primary,price_secondary,location,labels,comment,description,exchange,scrap_date".split(",")
        card_writer = csv.DictWriter(card_csvfile, fieldnames=card_fieldnames)
        card_writer.writeheader()

        card_gallery_fieldnames = "card_id,ind,url,scrap_date".split(",")
        card_gallery_writer = csv.DictWriter(card_gallery_csvfile, fieldnames=card_gallery_fieldnames)
        card_gallery_writer.writeheader()

        card_options_fieldnames = "card_id,category,item,scrap_date".split(",")
        card_options_writer = csv.DictWriter(card_options_csvfile, fieldnames=card_options_fieldnames)
        card_options_writer.writeheader()

        card_url_fieldnames = "card_id,url,scrap_date".split(",")
        card_url_writer = csv.DictWriter(card_url_csvfile, fieldnames=card_url_fieldnames)
        card_url_writer.writeheader()

        url_num = 0
        curr_year = int(time.strftime("%Y", time.gmtime()))

        for year in range(curr_year, 1900, -1):
            for price_usd in range(0, 500000, 10000):
                for page_num in range(1, 500):
                    url = f"{SITE_URL}/filter?year[min]={year}&year[max]={year}&price_usd[min]={price_usd}&price_usd[max]={price_usd+9999}&page={page_num}"
                    print(f"\ntime: {time.strftime('%X', time.gmtime(time.time() - start_time))}, url: {url}", file=log_file)

                    card_url_list = get_card_url_list(url)
                    if card_url_list == []:
                        print(f"time: {time.strftime('%X', time.gmtime(time.time() - start_time))}, no cards found", file=log_file)
                        break

                    for url in card_url_list:
                        url_num += 1
                        print(f"time: {time.strftime('%X', time.gmtime(time.time() - start_time))}, card: {url_num}, year: {year}: {url}")
                        print(f"time: {time.strftime('%X', time.gmtime(time.time() - start_time))}, card: {url_num}, year: {year}: {url}", file=log_file)

                        url_updated = url.replace("/","-").replace(".","-").replace(":","-")
                        card_id = url_updated.split("-")[-1]

                        parsed_card = get_parsed_card(url)

                        if parsed_card == {}:
                            continue

                        folder = make_folder(f"{os.curdir}", ["scrapped_data", "AV_BY", "JSON", f"{start_time_str}", f"{year}", f"price_{price_usd}-{price_usd+9999}"])
                        with open(f"{folder}/{url_updated}.json","w", encoding="utf-8") as f:
                            f.write(str(parsed_card).replace("\\xa0", " ").replace("\\u2009", " "))

                        parsed_card_csv = parsed_card.copy()
                        parsed_card_csv["card_id"] = card_id
                        del parsed_card_csv["gallery"]
                        del parsed_card_csv["options"]
                        del parsed_card_csv["json"]
                        for key,value in parsed_card_csv.items():
                            parsed_card_csv[key] = value.replace("\u00a0", " ").replace("\u2009", " ")
                        card_writer.writerow(parsed_card_csv)

                        card_url_csv_row = {"card_id": card_id, "url": url, "scrap_date": parsed_card["scrap_date"]}
                        card_url_writer.writerow(card_url_csv_row)

                        for img_ind, img_url in enumerate(parsed_card["gallery"]):
                            card_gallery_csv_row = {"card_id": card_id, "ind": img_ind + 1, "url": img_url, "scrap_date": parsed_card["scrap_date"]}
                            card_gallery_writer.writerow(card_gallery_csv_row)

                        for section in parsed_card["options"]:
                            category = section["category"]
                            for item in section["items"]:
                                card_options_csv_row = {"card_id": card_id, "category": category, "item": item, "scrap_date": parsed_card["scrap_date"]}
                                card_options_writer.writerow(card_options_csv_row)


        print(f"\nend time (GMT): {time.strftime('%X', time.gmtime())}", file=log_file)


if __name__ == "__main__":
    main()

