import base64
import io
import re
from bs4 import BeautifulSoup, Comment
import lxml
from PIL import Image

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from .gpt import LLM

def image_to_base64(pil_image, format='JPEG'):
    buffered = io.BytesIO()
    pil_image.save(buffered, format=format)
    image_bytes = buffered.getvalue()
    encoded_image = base64.b64encode(image_bytes).decode('utf-8')
    return encoded_image


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
        html_content = self.headless_driver.page_source

        soup = BeautifulSoup(html_content, 'lxml')

        for tag in soup(['script', 'style', 'link', 'svg']):
            tag.decompose()

        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        for tag in soup.find_all(True):
            if 'class' in tag.attrs:
                del tag.attrs['class']

        pretty_html = soup.prettify()

        with open("./tmp/html.html", "w", encoding='utf-8') as file:
            file.write(pretty_html)

        # Return the prettified HTML
        return pretty_html

    def screenshot(self, path: str = "./tmp/screenshot"):
        total_height = self.headless_driver.execute_script("return document.body.parentNode.scrollHeight")
        self.headless_driver.set_window_size(1920, total_height)
        self.headless_driver.save_screenshot(path + ".png")

        img = Image.open(path + ".png")
        img.save(path + ".jpg", "JPEG")
        jpg = Image.open(path + ".jpg")
        base64_img = image_to_base64(jpg)

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

