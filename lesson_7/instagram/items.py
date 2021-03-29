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


class UsersItem(scrapy.Item):
    _id = scrapy.Field()
    id = scrapy.Field()
    username = scrapy.Field()
    full_name = scrapy.Field()
    profile_pic_url = scrapy.Field()
    is_private = scrapy.Field()
    is_verified = scrapy.Field()


class FollowersItem(UsersItem):
    pass


class FollowingsItem(UsersItem):
    pass
