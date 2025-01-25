from browser.controller import BrowserController
from selenium.webdriver.common.by import By

def main():
    controller = BrowserController()
    controller.get("https://ics.uci.edu/")
    print(controller.html())

    print(controller.screenshot())
    controller.scroll_to(By.XPATH, "/html/body/div[1]/main/div/section[5]/div[2]/div[1]/div/div/div[2]/div/a")

    input()

if __name__ == "__main__":
    main()