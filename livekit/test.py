import asyncio
import time

from browser.controller import BrowserController

async def main():
    controller = BrowserController()
    controller.get("https://discord.com/channels/@me/1331877772443914333/1332816744435290152")

    start = time.perf_counter()
    await controller.table_of_contents()
    print(start - time.perf_counter())

if __name__ == "__main__":
    asyncio.run(main())
