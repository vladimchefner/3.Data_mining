from datetime import datetime
from urllib.parse import urlencode

from ..items import InstaTagItem, InstaPostItem
import scrapy
import json


class InstagramSpider(scrapy.Spider):
    name = "instagram"
    allowed_domains = ["www.instagram.com"]
    start_urls = ["http://www.instagram.com/"]
    _login_url = "https://www.instagram.com/accounts/login/ajax/"
    _tags_path = "/explore/tags/"
    _api_url = "/graphql/query/"

    def __init__(self, login, password, tags, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = login
        self.password = password
        self.tags = tags

    def parse(self, response, *args, **kwargs):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self._login_url,
                method="POST",
                callback=self.parse,
                formdata={"username": self.login, "enc_password": self.password},
                headers={"X-CSRFToken": js_data["config"]["csrf_token"]},
            )
        except AttributeError:
            if response.json()["authenticated"]:
                for tag_name in self.tags:
                    yield response.follow(
                        f"{self._tags_path}{tag_name}/", callback=self.tag_page_parse
                    )

    def tag_page_parse(self, response):
        js_data = self.js_data_extract(response)
        insta_tag = InstTag(js_data["entry_data"]["TagPage"][0]["graphql"]["hashtag"])
        yield insta_tag.get_tag_item()
        yield from insta_tag.get_post_items()
        yield response.follow(
            f"{self._api_url}?{urlencode(insta_tag.paginate_params())}",
            callback=self._api_tag_parse,
        )

    def _api_tag_parse(self, response):
        data = response.json()
        insta_tag = InstTag(data["data"]["hashtag"])
        yield from insta_tag.get_post_items()
        yield response.follow(
            f"{self._api_url}?{urlencode(insta_tag.paginate_params())}",
            callback=self._api_tag_parse,
        )

    def js_data_extract(self, response):
        script = (
            response.xpath("//script[contains(text(), 'window._sharedData =')]/text()")
            .extract_first()
            .replace("window._sharedData = ", "")[:-1]
        )
        return json.loads(script)


class InstTag:
    query_hash = "9b498c08113f1e09617a1703c22b2f32"

    def __init__(self, hashtag: dict):
        self.hashtag = hashtag
        self.variables = {
            "tag_name": hashtag["name"],
            "first": 100,
            "after": hashtag["edge_hashtag_to_media"]["page_info"]["end_cursor"],
        }

    def get_tag_item(self):
        item = InstaTagItem()
        item["date_parse"] = datetime.utcnow()
        data = {}
        for key, value in self.hashtag.items():
            if not (isinstance(value, dict) or isinstance(value, list)):
                data[key] = value
        item["data"] = data
        return item

    def paginate_params(self):
        url_query = {"query_hash": self.query_hash, "variables": json.dumps(self.variables)}
        return url_query

    def get_post_items(self):
        for edge in self.hashtag["edge_hashtag_to_media"]["edges"]:
            yield InstaPostItem(date_parse=datetime.utcnow(), data=edge["node"])
