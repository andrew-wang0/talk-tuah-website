from selenium import webdriver

class BrowserController:
    def __init__(self):
        self.driver = webdriver.Chrome()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()

    def get(self, url):
        self.driver.get(url)

    def html(self):
        return self.driver.page_source

