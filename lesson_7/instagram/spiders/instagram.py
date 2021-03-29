import scrapy
import json
from ..items import FollowersItem, FollowingsItem


class InstagramSpider(scrapy.Spider):
    name = "instagram"
    allowed_domains = ["www.instagram.com"]
    start_urls = ["http://www.instagram.com/"]
    _authorization = "https://www.instagram.com/accounts/login/ajax/"
    _api_path = "https://www.instagram.com/graphql/query/"
    _queries_hash = ["5aefa9893005572d237da5068082d8d5", "3dec7e2c57367ef3da3d987d89f9dbc8"]
    _items = [FollowersItem, FollowingsItem]
    user = ""

    def __init__(self, login, password, users, **kwargs):
        super().__init__(**kwargs)
        self.login = login
        self.password = password
        self.users = users

    def get_json_data(self, response):
        return json.loads(
            response.xpath("//script[contains(text(), 'window._sharedData')]/text()")
            .get()
            .split("window._sharedData = ")[1][:-1]
        )

    def get_api_url(self, user_id, query_hash, after):
        variables = {
            "id": user_id,
            "include_reel": "true",
            "fetch_mutual": "false",
            "first": 100,
            "after": after,
        }
        return f"{self._api_path}?query_hash={query_hash}&variables={json.dumps(variables)}"

    def get_end_cursor_and_people_list(self, js_data, query_hash):
        return (
            [
                js_data["data"]["user"]["edge_followed_by"]["page_info"]["end_cursor"],
                js_data["data"]["user"]["edge_followed_by"]["edges"],
            ]
            if query_hash == self._queries_hash[0]
            else [
                js_data["data"]["user"]["edge_follow"]["page_info"]["end_cursor"],
                js_data["data"]["user"]["edge_follow"]["edges"],
            ]
        )

    def parse(self, response, *args, **kwargs):
        try:
            js_data = self.get_json_data(response)
            yield scrapy.FormRequest(
                self._authorization,
                method="POST",
                formdata={"username": self.login, "enc_password": self.password},
                headers={"X-CSRFToken": js_data["config"]["csrf_token"]},
                callback=self.parse,
            )
        except AttributeError:
            for user in self.users:
                yield response.follow(
                    f"{self.start_urls[0]}{user}/",
                    callback=self.user_parse,
                    cb_kwargs={"user": user},
                )

    def user_parse(self, response, **kwargs):
        js_data = self.get_json_data(response)
        user_id = js_data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["id"]
        for query_hash, item_class in zip(self._queries_hash, self._items):
            yield response.follow(
                self.get_api_url(user_id, query_hash, after=""),
                callback=self.pagination_parse,
                cb_kwargs={
                    "user_id": user_id,
                    "query_hash": query_hash,
                    "item": item_class,
                    "user": kwargs["user"],
                },
            )

    def pagination_parse(self, response, **kwargs):
        js_data = response.json()
        end_cursor, people = self.get_end_cursor_and_people_list(js_data, kwargs["query_hash"])
        for person in people:
            yield self.people_parse(person["node"], kwargs["item"], kwargs["user"])
        if end_cursor:
            yield response.follow(
                self.get_api_url(kwargs["user_id"], kwargs["query_hash"], after=end_cursor),
                callback=self.pagination_parse,
                cb_kwargs={
                    "user_id": kwargs["user_id"],
                    "item": kwargs["item"],
                    "user": kwargs["user"],
                    "query_hash": kwargs["query_hash"],
                },
            )

    def people_parse(self, person, item_class, username):
        self.user = username
        item = item_class()
        for key, value in person.items():
            try:
                item[key] = value
            except KeyError:
                pass
        return item
