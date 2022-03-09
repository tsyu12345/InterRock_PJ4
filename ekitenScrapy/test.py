import imp
from click import option
from selenium import webdriver

def restart_driver(driver:webdriver.Chrome, options:webdriver.ChromeOptions) -> webdriver.Chrome:
    driver.quit()
    new_driver = webdriver.Chrome(executable_path='../chromedriver.exe', options=options)
    return new_driver

if __name__ == "__main__":
    browser_path = '../chrome-win/chrome.exe'
    options = webdriver.ChromeOptions()
    options.binary_location = browser_path
    driver:webdriver.Chrome = webdriver.Chrome(executable_path='../chromedriver.exe', options=options)
    print("get...")
    driver = restart_driver(driver, options=options)
    print("get new driver")
    driver.get("https://www.google.com")   