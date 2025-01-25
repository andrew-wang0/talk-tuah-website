from browser.controller import BrowserController

controller = BrowserController()
controller.get("https://ics.uci.edu/")
print(controller.html())

input()
