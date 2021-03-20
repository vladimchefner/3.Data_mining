# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AutoYoulaItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    images = scrapy.Field()
    characteristics = scrapy.Field()
    description = scrapy.Field()
    author_url = scrapy.Field()
    phone = scrapy.Field()


class HhVacancyItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    description = scrapy.Field()
    skills = scrapy.Field()
    employer = scrapy.Field()


class HhEmployerItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()
    site_url = scrapy.Field()
    activity = scrapy.Field()
    description = scrapy.Field()
