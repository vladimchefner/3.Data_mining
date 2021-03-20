from scrapy.loader import ItemLoader
from .items import AutoYoulaItem, HhVacancyItem, HhEmployerItem
from itemloaders.processors import TakeFirst, MapCompose, Join
from scrapy import Selector
from base64 import b64decode


def get_characteristics(item):
    selector = Selector(text=item)
    return {
        selector.xpath("//div[contains(@class, 'AdvertSpecs_label')]/text()")
        .get(): selector.xpath("//div[contains(@class, 'AdvertSpecs_data')]//text()")
        .get()
    }


def get_author_url(item):
    end = item[0].find("%22%2C%22avatar")
    if end == -1:
        start = item[0].rfind("youlaId%22%2C%22") + 16
        end = item[0].find("%22%2C%22alias")
        return f"https://youla.ru/user/{item[0][start:end]}"
    start = item[0].rfind("youlaId%22%2C%22") + 16
    return f"https://youla.ru/user/{item[0][start:end]}"


def get_phone(item):
    start = item[0].find("phone%22%2C%22") + 14
    end = item[0].find("%3D%3D%22%2C%22")
    return b64decode(b64decode(f"{item[0][start:end]}==")).decode("utf-8")


class AutoYoulaLoaders(ItemLoader):
    default_item_class = AutoYoulaItem
    url_out = TakeFirst()
    title_out = TakeFirst()
    price_out = TakeFirst()
    characteristics_in = MapCompose(get_characteristics)
    description_out = TakeFirst()
    author_url_out = get_author_url
    phone_out = get_phone


def get_description(item):
    return "\n".join(item)


def get_url(item):
    return f"https://hh.ru{item[0]}"


class HhVacancyLoaders(ItemLoader):
    default_item_class = HhVacancyItem
    url_out = TakeFirst()
    title_out = TakeFirst()
    salary_out = Join()
    description_out = get_description
    employer_out = get_url


class HhEmployerLoaders(ItemLoader):
    default_item_class = HhEmployerItem
    url_out = TakeFirst()
    name_out = Join()
    site_url_out = TakeFirst()
    description_out = get_description
