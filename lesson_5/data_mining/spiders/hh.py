import scrapy
from ..xpath_selectors import (
    _hh_main_xpath,
    _hh_vacancy_xpath,
    _hh_employer_xpath,
    _hh_employer_vacancy_xpath,
)
from ..loaders import HhVacancyLoaders, HhEmployerLoaders


class HhSpider(scrapy.Spider):
    name = "hh"
    allowed_domain = ["hh.ru"]
    start_urls = ["https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113"]

    def get_follow(self, response, template, callback):
        for link in response.xpath(template):
            yield response.follow(link, callback=callback)

    def parse(self, response, **kwargs):
        callbacks = {
            "pagination": self.parse,
            "vacancy": self.vacancy_parse,
            "employer": self.employer_parse,
        }
        for key, value in _hh_main_xpath.items():
            yield from self.get_follow(response, value, callbacks[key])

    def vacancy_parse(self, response):
        loader = HhVacancyLoaders(response=response)
        loader.add_value("url", response.url)
        for label, xpath in _hh_vacancy_xpath.items():
            loader.add_xpath(label, xpath)
        yield loader.load_item()

    def employer_parse(self, response):
        loader = HhEmployerLoaders(response=response)
        loader.add_value("url", response.url)
        for label, xpath in _hh_employer_xpath.items():
            loader.add_xpath(label, xpath)
        yield loader.load_item()
        yield from self.get_follow(response, _hh_employer_vacancy_xpath, self.vacancy_parse)
