import asyncio
import time

from .controller import BrowserController

async def main():
    controller = BrowserController()
    controller.get("https://ics.uci.edu/")

    start = time.perf_counter()
    md = await controller.table_of_contents()
    print(start - time.perf_counter())
    print(md)

    input()

if __name__ == "__main__":
    asyncio.run(main())
