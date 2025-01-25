from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from llm import LLM

class BrowserController:
    def __init__(self):
        headless_options = Options()
        headless_options.add_argument("--window-size=1920,1080")
        headless_options.add_argument("--headless")
        headless_options.add_argument("--disable-gpu")
        self.headless_driver = webdriver.Chrome(options=headless_options)

        options = Options()
        options.add_argument("--window-size=1920,1080")
        self.driver = webdriver.Chrome(options=options)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.headless_driver.quit()
        self.driver.quit()

    def __del__(self):
        self.headless_driver.quit()
        self.driver.quit()

    def get(self, url: str):
        self.headless_driver.get(url)
        self.driver.get(url)
        total_height = self.headless_driver.execute_script("return document.body.parentNode.scrollHeight")
        self.headless_driver.set_window_size(1920, total_height)

    def html(self):
        return self.headless_driver.page_source

    def screenshot(self, path: str = "./tmp/screenshot.png"):
        total_height = self.headless_driver.execute_script("return document.body.parentNode.scrollHeight")
        self.headless_driver.set_window_size(1920, total_height)
        self.headless_driver.save_screenshot(path)
        base64_img = self.headless_driver.get_screenshot_as_base64()

        return base64_img

    def scroll_to(self, by: By, value: str):
        scroll = "arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });"

        element = self.headless_driver.find_element(by, value)
        self.headless_driver.execute_script(scroll, element)

        element = self.driver.find_element(by, value)
        self.driver.execute_script(scroll, element)

    def scroll_up(self, pixels: int = 500):
        scroll_script = f"window.scrollBy({{ top: -{pixels}, left: 0, behavior: 'smooth' }});"
        self.headless_driver.execute_script(scroll_script)
        self.driver.execute_script(scroll_script)

    def scroll_down(self, pixels: int = 500):
        scroll_script = f"window.scrollBy({{ top: {pixels}, left: 0, behavior: 'smooth' }});"
        self.headless_driver.execute_script(scroll_script)
        self.driver.execute_script(scroll_script)

    def scroll_top(self):
        self.headless_driver.execute_script("window.scrollTo(0, 0);")
        self.driver.execute_script("window.scrollTo(0, 0);")

    def scroll_bottom(self):
        self.headless_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def click(self, by: By, value: str):
        element = self.headless_driver.find_element(by, value)
        element.click()

        element = self.driver.find_element(by, value)
        element.click()

    def type(self, by: By, value: str, keys: str):
        element = self.headless_driver.find_element(by, value)
        element.send_keys(keys)

        element = self.driver.find_element(by, value)
        element.send_keys(keys)

    async def table_of_contents(self):
        img = self.screenshot()
        llm = LLM()
        toc = await llm.table_of_contents(self.html(), img)

        with open("./tmp/toc.md", "w") as file:
            file.write(toc)

        return toc

