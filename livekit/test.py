import asyncio
import time

from browser.controller import BrowserController

async def main():
    controller = BrowserController()
    controller.get("https://www.nytimes.com/")

    start = time.perf_counter()
    await controller.table_of_contents()
    print(start - time.perf_counter())

if __name__ == "__main__":
    asyncio.run(main())
