# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaItem(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field()
    photos = scrapy.Field()


class InstaTagItem(InstaItem):
    pass


class InstaPostItem(InstaItem):
    pass
