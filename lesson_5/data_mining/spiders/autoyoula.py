import scrapy
from ..xpath_selectors import (
    _autoyola_brand_name_xpath,
    _autoyoula_brand_xpaths,
    _autoyoula_car_xpaths,
)
from ..loaders import AutoYoulaLoaders


class AutoyoulaSpider(scrapy.Spider):
    name = "autoyoula"
    allowed_domains = ["auto.youla.ru"]
    start_urls = ["https://auto.youla.ru/"]

    def _get_follow(self, response, select_str, callback):
        for link in response.xpath(select_str):
            yield response.follow(link, callback=callback)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(
            response, _autoyola_brand_name_xpath["brands"], self.brand_parse
        )

    def brand_parse(self, response):
        callbacks = {"pagination": self.brand_parse, "car": self.car_parse}
        for key, value in _autoyoula_brand_xpaths.items():
            yield from self._get_follow(response, value, callbacks[key])

    def car_parse(self, response):
        loader = AutoYoulaLoaders(response=response)
        loader.add_value("url", response.url)
        for key, xpath in _autoyoula_car_xpaths.items():
            loader.add_xpath(key, xpath)
        yield loader.load_item()
