from base64 import b64decode

import pymongo
import scrapy


class AutoyoulaSpider(scrapy.Spider):
    name = "autoyoula"
    allowed_domains = ["auto.youla.ru"]
    start_urls = ["https://auto.youla.ru/"]
    _css_selector = {
        "brands": ".TransportMainFilters_brandsList__2tIkv .ColumnItemList_container__5gTrc a.blackLink",
        "pagination": "a.Paginator_button__u1e7D",
        "car": ".SerpSnippet_titleWrapper__38bZM a.SerpSnippet_titleText__1Ex8A",
        "name": ".AdvertCard_advertTitle__1S1Ak::text",
        "image": "figure.PhotoGallery_photo__36e_r img::attr(src)",
        "char": [
            "div.AdvertCard_specs__2FEHc .AdvertSpecs_row__ljPcX",
            ".AdvertSpecs_label__2JHnS::text",
            ".AdvertSpecs_data__xK2Qx::text",
            ".AdvertSpecs_data__xK2Qx a::text",
        ],
        "description": ".AdvertCard_descriptionInner__KnuRi::text",
        "price": ".AdvertCard_priceBlock__1hOQW .AdvertCard_price__3dDCr::text",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_client = pymongo.MongoClient()

    def _get_follow(self, response, select_str, callback, **kwargs):
        for a in response.css(select_str):
            link = a.attrib.get("href")
            yield response.follow(link, callback=callback, cb_kwargs=kwargs)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(response, self._css_selector["brands"], self.brand_parse)

    def brand_parse(self, response):
        yield from self._get_follow(response, self._css_selector["pagination"], self.brand_parse)
        yield from self._get_follow(response, self._css_selector["car"], self.car_parse)

    def car_parse(self, response):
        auto_data = dict()
        for key, value in self.data_car_template().items():
            try:
                auto_data[key] = value(response)
            except (AttributeError, ValueError):
                pass
        self.db_client["Data_mining"][self.name].insert_one(auto_data)

    def data_car_template(self):
        data = {
            "name": lambda r: r.css(self._css_selector["name"]).extract_first(),
            "image": lambda r: r.css(self._css_selector["image"]).extract(),
            "characteristics": lambda r: [
                {
                    para.css(self._css_selector["char"][1])
                    .extract_first(): para.css(self._css_selector["char"][2])
                    .extract_first()
                    or para.css(self._css_selector["char"][3]).extract_first()
                }
                for para in r.css(self._css_selector["char"][0])
            ],
            "description": lambda r: r.css(self._css_selector["description"]).get(),
            "price": lambda r: r.css(self._css_selector["price"]).get(),
            "author": lambda r: self._get_data_from_script(r, "author"),
            "phone": lambda r: self._get_data_from_script(r, "phone"),
        }
        return data

    @staticmethod
    def _get_data_from_script(response, key):
        for script in response.css("script::text").extract():
            if "window.transitState = decodeURIComponent" in script:
                if key == "phone":
                    start = script.find("phone%22%2C%22") + 14
                    end = script.find("%3D%3D%22%2C%22")
                    return b64decode(b64decode(f"{script[start:end]}==")).decode("utf-8")
                else:
                    end = script.find("%22%2C%22avatar")
                    if end == -1:
                        start = script.rfind("youlaId%22%2C%22") + 16
                        end = script.find("%22%2C%22alias")
                        return response.urljoin(f"/user/{script[start:end]}")
                    start = script.rfind("youlaId%22%2C%22") + 16
                    return response.urljoin(f"/user/{script[start:end]}")
