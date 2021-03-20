_autoyola_brand_name_xpath = {
    "brands": "//div[@data-target='transport-main-filters']//a[@class='blackLink']/@href"
}
_autoyoula_brand_xpaths = {
    "pagination": "//a[@data-target-id='button-link-serp-paginator']/@href",
    "car": "//a[@data-target='serp-snippet-title']/@href",
}
_autoyoula_car_xpaths = {
    "title": "//div[@data-target='advert-title']/text()",
    "price": "//div[@data-target='advert-price']/text()",
    "images": "//img[contains(@class, 'PhotoGallery_photoImage')]/@src",
    "characteristics": "//h3[contains(text(), 'Характеристики')]/..//"
    "div[contains(@class, 'AdvertSpecs_row')]",
    "description": "//div[@data-target='advert-info-descriptionFull']/text()",
    "author_url": "//script[contains(text(), 'window.transitState = decodeURIComponent')]",
    "phone": "//script[contains(text(), 'window.transitState = decodeURIComponent')]",
}
_hh_main_xpath = {
    "pagination": "//div[@data-qa='pager-block']//a[@data-qa='pager-page']/@href",
    "vacancy": "//div[@class='vacancy-serp']//a[@data-qa='vacancy-serp__vacancy-title']/@href",
    "employer": "//div[@class='vacancy-serp']//a[@data-qa='vacancy-serp__vacancy-employer']/@href",
}
_hh_vacancy_xpath = {
    "title": "//h1[@data-qa='vacancy-title']/text()",
    "salary": "//p[@class='vacancy-salary']//text()",
    "description": "//div[@class='vacancy-description']//text()",
    "skills": "//div[@class='bloko-tag-list']//text()",
    "employer": "//a[@class='vacancy-company-name']/@href",
}
_hh_employer_xpath = {
    "name": "//div[@class='company-header']//text()",
    "site_url": "//a[@data-qa='sidebar-company-site']/@href",
    "activity": "//div[contains(text(), 'Сферы деятельности')]/../p/text()",
    "description": "//div[@class='g-user-content']//text()",
}
_hh_employer_vacancy_xpath = (
    "//h3[contains(text(), 'Вакансии компании')]/..//"
    "a[@data-qa='vacancy-serp__vacancy-title']/@href"
)
