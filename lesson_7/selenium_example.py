from selenium import webdriver
from selenium.webdriver.common.keys import Keys


if __name__ == "__main__":
    url = "https://habr.com/ru/"
    browser = webdriver.Firefox(executable_path="C:\\WebDriver\\bin\\geckodriver")
    browser.get(url)
    c = 1
