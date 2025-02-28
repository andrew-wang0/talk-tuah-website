import base64
import io
from bs4 import BeautifulSoup, Comment
from PIL import Image

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from .gpt import LLM
from pathlib import Path

def image_to_base64(pil_image, format='JPEG'):
    buffered = io.BytesIO()
    pil_image.save(buffered, format=format)
    image_bytes = buffered.getvalue()
    encoded_image = base64.b64encode(image_bytes).decode('utf-8')
    return encoded_image


def find_tmp_folder():
    current_dir = Path.cwd()
    tmp_folders = list(current_dir.rglob('tmp')) 
    tmp_folders = [folder.resolve() for folder in tmp_folders if folder.is_dir()]
    
    if tmp_folders:
        return str(tmp_folders[0])
    else:
        tmp_folder = current_dir / 'tmp'
        tmp_folder.mkdir(parents=True, exist_ok=True)
        return str(tmp_folder)


class BrowserController:
    def __init__(self):
        self.tmp = find_tmp_folder()

        headless_options = Options()
        headless_options.add_argument("--window-size=1920,1080")
        headless_options.add_argument("--headless")
        headless_options.add_argument("--disable-gpu")
        self.headless_driver = webdriver.Chrome(options=headless_options)

        options = Options()
        options.add_argument("--window-size=860,1080")
        options.add_argument(f"--window-position={0},{0}")
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

        for tag in soup(['script', 'style', 'link', 'svg', 'iframe', 'noscript']):
            tag.decompose()

        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        for tag in soup.find_all(True):
            if 'class' in tag.attrs:
                del tag.attrs['class']

        text_limit = 500
        for text_node in soup.find_all(string=True):
            if not text_node.strip():
                continue
            if len(text_node) > text_limit:
                truncated_text = text_node[:text_limit] + '...'
                text_node.replace_with(truncated_text)

        for tag in reversed(soup.find_all()):
            if tag.name in ['img', 'button', 'input', 'select', 'textarea']:
                continue
            if not tag.find(True) and not tag.get_text(strip=True):
                tag.decompose()

        pretty_html = soup.prettify()

        with open(f"{self.tmp}/html.html", "w", encoding='utf-8') as file:
            file.write(pretty_html)

        return pretty_html

    def screenshot(self):
        base = f"{self.tmp}/screenshot"
        total_height = self.headless_driver.execute_script("return document.body.parentNode.scrollHeight")
        self.headless_driver.set_window_size(1920, total_height)
        self.headless_driver.save_screenshot(base + ".png")

        img = Image.open(base + ".png")
        img.save(base + ".jpg", "JPEG")
        jpg = Image.open(base + ".jpg")
        base64_img = image_to_base64(jpg)

        return base64_img

    def scroll_to(self, by: By, value: str, highlight: bool = True):
        scroll = "arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });"

        try:
            element = self.driver.find_element(by, value)
        except:
            print("[[SCROLL_TO]] ELEMENT NOT FOUND")
            return
        print("[[SCROLL_TO]] ELEMENT FOUND")


        print(f"[[SCROLL_TO]] SCROLLING TO {element}")
        self.driver.execute_script(scroll, element)

        if highlight:
            self.driver.execute_script("arguments[0].style.backgroundColor = 'yellow';", element)


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

    async def generate_table_of_contents(self):
        img = self.screenshot()
        llm = LLM()
        toc = await llm.table_of_contents(self.html(), img)

        with open(f"{self.tmp}/toc.md", "w") as file:
            file.write(toc)
        
        print("[[LOG]]:", "Generated TOC")

        return toc

    def get_table_of_contents(self):
        with open(f"{self.tmp}/toc.md") as f:
            return f.read()

    async def generate_contents(self):
        img = self.screenshot()
        llm = LLM()
        toc = await llm.contents(self.html(), self.get_table_of_contents(), img)

        with open(f"{self.tmp}/contents.md", "w") as file:
            file.write(toc)

        print("[[LOG]]:", "Generated Contents")

        return toc

    def get_contents(self):
        with open(f"{self.tmp}/contents.md") as f:
            return f.read()
