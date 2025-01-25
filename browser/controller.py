from selenium import webdriver

class BrowserController:
    def __init__(self):
        self.driver = webdriver.Chrome()

    def get(self, url):
        self.driver.get(url)

