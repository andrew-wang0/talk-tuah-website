import asyncio
import time

from browser.controller import BrowserController

async def main():
    controller = BrowserController()
    controller.get("https://larc.uci.edu/")

    start = time.perf_counter()
    await controller.generate_table_of_contents()
    print(time.perf_counter() - start)

    start = time.perf_counter()
    await controller.generate_contents()
    print(time.perf_counter() - start)

if __name__ == "__main__":
    asyncio.run(main())
