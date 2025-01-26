import asyncio
import time

from selenium.webdriver.common.by import By

from browser.controller import BrowserController

async def main():
    controller = BrowserController()
    controller.get("https://larc.uci.edu/")

    # xpath = "//*[contains(normalize-space(text()), 'Have tough homework?')]"
    # controller.scroll_to(By.XPATH, xpath)

    start = time.perf_counter()
    await controller.generate_table_of_contents()
    print(time.perf_counter() - start)

    start = time.perf_counter()
    await controller.generate_contents()
    print(time.perf_counter() - start)

    input()

if __name__ == "__main__":
    asyncio.run(main())

# navigate to larc.uci.edu
# tell me the first testimonial