from requests import get
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
from database.create_post import Database


class ParsePost:
    def __init__(self, first_url, to_save):
        self.first_url = first_url
        self.db = to_save
        self.done_urls_page = {
            self.first_url,
        }
        self.done_urls_posts = set()
        self.tasks = [
            self.get_task(self.first_url, self.parse_feed),
        ]

    def get_task(self, url, cb):
        def task():
            return cb(url, self._get_soup(url))

        return task

    def _get_response(self, url):
        return get(url)

    def _get_soup(self, url):
        return BeautifulSoup(self._get_response(url).text, "lxml")

    def _parse_feed_template(self, url, soup, **kwargs):
        items = soup.find(kwargs["tag"], attrs={kwargs["attr1_key"]: kwargs["attr1_val"]})
        for a in items.find_all("a", attrs={kwargs["attr2_key"]: kwargs["attr2_val"]}):
            item_url = urljoin(url, a.attrs.get("href"))
            if item_url not in kwargs["set"]:
                kwargs["set"].add(item_url)
                self.tasks.append(self.get_task(item_url, kwargs["task"]))

    def parse_feed(self, url, soup):
        d_page = {
            "tag": "ul",
            "attr1_key": "class",
            "attr1_val": "gb__pagination",
            "attr2_key": "href",
            "attr2_val": True,
            "set": self.done_urls_page,
            "task": self.parse_feed,
        }
        d_post = {
            "tag": "div",
            "attr1_key": "class",
            "attr1_val": "post-items-wrapper",
            "attr2_key": "class",
            "attr2_val": "post-item__title",
            "set": self.done_urls_posts,
            "task": self.parse_post,
        }
        self._parse_feed_template(url, soup, **d_page)
        self._parse_feed_template(url, soup, **d_post)

    def parse_post(self, url, soup):
        data = {
            "post_data": {
                "id": soup.find("comments").attrs.get("commentable-id"),
                "title": soup.find("h1", attrs={"class": "blogpost-title"}).text,
                "url": url,
                "img": soup.find("div", attrs={"class": "hidden", "itemprop": "image"}).text,
                "created_at": datetime.fromisoformat(
                    soup.find("time", attrs={"itemprop": "datePublished"}).attrs.get("datetime")
                ),
            },
            "author_data": {
                "id": soup.find("div", attrs={"itemprop": "author"}).parent.attrs.get("href")[7:],
                "full_name": soup.find("div", attrs={"itemprop": "author"}).text,
                "url": urljoin(
                    url, soup.find("div", attrs={"itemprop": "author"}).parent.attrs.get("href")
                ),
            },
            "tags_data": [
                {"name": tag.text, "url": urljoin(url, tag.attrs.get("href"))}
                for tag in soup.find_all("a", attrs={"class": "small"})
            ],
            "comments_data": self._get_comment(soup.find("comments").attrs.get("commentable-id")),
        }
        return data

    def _get_comment(self, post_id):
        api = f"/api/v2/comments?commentable_type=Post&commentable_id={post_id}&order=desc"
        return self._get_response(urljoin(self.first_url, api)).json()

    def run(self):
        for task in self.tasks:
            task_res = task()
            if task_res:
                self._save(task_res)

    def _save(self, data):
        self.db.create_post(data)


if __name__ == "__main__":
    parser = ParsePost("https://geekbrains.ru/posts/", Database("sqlite:///gb_blog.db"))
    parser.run()
