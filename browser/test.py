import asyncio

from browser.controller import BrowserController
from selenium.webdriver.common.by import By

async def main():
    controller = BrowserController()
    controller.get("https://ics.uci.edu/")
    print(await controller.table_of_contents())

    input()

if __name__ == "__main__":
    asyncio.run(main())
