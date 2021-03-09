import datetime
from urllib.parse import urljoin
import bs4
import pymongo
import requests

mon = {
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июля": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12,
}


class MagnitParse:
    def __init__(self, promo_url, to_save):
        self.url = promo_url
        self.mongodb_save = to_save["Data_mining"]
        self.collections = self.mongodb_save["Magnit_promo_parse"]

    def run(self):
        soup = self._get_soup(self.url)
        catalog = soup.find("div", attrs={"class": "сatalogue__main"})
        for product in catalog.find_all("a", attrs={"class": "card-sale", "target": False}):
            product_info = self._parse(product)
            self._save(product_info)

    def _get_response(self, promo_url):
        return requests.get(promo_url)

    def _get_soup(self, promo_url):
        response = self._get_response(promo_url)
        return bs4.BeautifulSoup(response.text, "lxml")

    def _parse(self, product):
        data = {}
        for key, value in self.get_template().items():
            try:
                data[key] = value(product)
            except (AttributeError, ValueError):
                pass
        return data

    def get_template(self):
        return {
            "url": lambda n: urljoin(self.url, n.attrs.get("href", "")),
            "promo_name": lambda n: n.find("div", attrs={"class": "card-sale__header"}).text,
            "product_name": lambda n: n.find("div", attrs={"class": "card-sale__title"}).text,
            "old_price": lambda n: float(
                n.find("div", attrs={"class": "label__price_old"}).text.strip().replace("\n", ".")
            ),
            "new_price": lambda n: float(
                ".".join(n.find("div", attrs={"class": "label__price_new"}).text.split())
            ),
            "image_url": lambda n: urljoin(self.url, n.find("img").attrs.get("data-src")),
            "date_from": lambda n: self._get_date(
                n.find("div", attrs={"class": "card-sale__date"}).text.strip().split("\n")[0]
            ),
            "date_to": lambda n: self._get_date(
                n.find("div", attrs={"class": "card-sale__date"}).text.strip().split("\n")[-1]
            ),
        }

    def _get_date(self, date_text):
        y = int(datetime.datetime.today().strftime("%Y"))
        m = int(mon[date_text.split()[-1]])
        d = int(date_text.split()[1])
        return str(datetime.date(y, m, d))

    def _save(self, data):
        self.collections.insert_one(data)


if __name__ == "__main__":
    url = "https://magnit.ru/promo/"
    db_client = pymongo.MongoClient("mongodb://localhost:27017")
    parser = MagnitParse(url, db_client)
    parser.run()
