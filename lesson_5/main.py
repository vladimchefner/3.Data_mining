from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from data_mining.spiders.autoyoula import AutoyoulaSpider
from data_mining.spiders.hh import HhSpider

if __name__ == "__main__":
    crawler_setting = Settings()
    crawler_setting.setmodule("data_mining.settings")
    crawler_proc = CrawlerProcess(settings=crawler_setting)
    crawler_proc.crawl(HhSpider)
    crawler_proc.start()
