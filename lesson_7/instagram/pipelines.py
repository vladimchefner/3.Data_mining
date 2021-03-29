# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from lesson_7.instagram.spiders.instagram import InstagramSpider


class InstaPipeline:
    def __init__(self):
        client = MongoClient()
        self.db = client["Instagram"]

    def process_item(self, item, spider):
        self.db[f"{spider.user}/{type(item).__name__.split('Item')[0]}"].insert_one(item)
        return item


class ImageDownloadPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for url in item.get("photos", []):
            yield Request(url)
        image = item["data"].get("profile_pic_url") or item["data"].get("display_url")
        if image:
            yield Request(image)

    def item_completed(self, results, item, info):
        if results:
            item["photos"] = [itm[1] for itm in results]
        return item
