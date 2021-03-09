from pathlib import Path
import requests
import time
import json


class Parse5ka:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/78.0.3904.97 Safari/537.36 OPR/65.0.3467.48"
    }
    params = {
        "store": None,
        "records_per_page": 12,
        "page": 1,
        "categories": None,
        "ordering": None,
        "price_promo__gte": None,
        "price_promo__lte": None,
        "search": None,
    }

    def __init__(self, sp_off_url: str, save_path: Path):
        self.sp_off_url = sp_off_url
        self.save_path = save_path

    def _get_response(self, sp_off_url):
        while True:
            response = requests.get(sp_off_url, headers=self.headers)
            if response.status_code == 200:
                return response
            time.sleep(0.5)

    def run(self):
        for product in self._parse(self.sp_off_url):
            product_path = self.save_path.joinpath(f"{product['id']}.json")
            self._save(product, product_path)

    def _parse(self, sp_off_url):
        while sp_off_url:
            response = self._get_response(sp_off_url)
            data = response.json()
            sp_off_url = data["next"]
            for product in data["results"]:
                yield product

    @staticmethod
    def _save(data: dict, file_path: Path):
        file_path.write_text(json.dumps(data, ensure_ascii=False))


class Parse5kaCat(Parse5ka):
    def __init__(self, sp_off_url: str, cat_url: str, save_path: Path):
        super().__init__(sp_off_url, save_path)
        self.cat_url = cat_url

    def _get_categories(self):
        response = self._get_response(self.cat_url)
        categories = response.json()
        for category in categories:
            yield category

    def run(self):
        for category in self._get_categories():
            self.params["categories"] = category["parent_group_code"]
            sp_off_cat_url = requests.get(sp_off_url, params=self.params).url
            category["products"] = []
            for product in self._parse(sp_off_cat_url):
                category["products"].append(product)
            dir_name = f"{category['parent_group_name']}.json"
            cat_path = self.save_path.joinpath(dir_name)
            self._save(category, cat_path)


def get_save_path(directory_name: str):
    save_path = Path(__file__).parent.joinpath(directory_name)
    if not save_path.exists():
        save_path.mkdir()
    return save_path


if __name__ == "__main__":
    sp_off_url = "https://5ka.ru/api/v2/special_offers/"
    cat_url = "https://5ka.ru/api/v2/categories/"
    save_path_prod = get_save_path("products")
    save_path_cat = get_save_path("categories")
    parser_prod = Parse5ka(sp_off_url, save_path_prod)
    parser_prod.run()
    pars_cat = Parse5kaCat(sp_off_url, cat_url, save_path_cat)
    pars_cat.run()
