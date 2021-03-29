from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from lesson_7.instagram.spiders.instagram import InstagramSpider
import os
import dotenv


if __name__ == "__main__":
    dotenv.load_dotenv(".env")
    crawler_settings = Settings()
    users = [
        "vladimchefner",
    ]
    crawler_settings.setmodule("instagram.settings")
    crawler_proc = CrawlerProcess(settings=crawler_settings)
    crawler_proc.crawl(
        InstagramSpider,
        login=os.getenv("INST_LOGIN"),
        password=os.getenv("INST_PASSWORD"),
        users=users,
    )
    crawler_proc.start()
