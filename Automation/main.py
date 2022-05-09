from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import time

service = Service('/Users/hhvn/Downloads/chromedriver')


def get_driver():
    # Set options to make browsing easier
    options = webdriver.ChromeOptions()
    options.add_argument("disable-infobars")
    options.add_argument("start-maximized")
    options.add_argument("disable-dev-shm-usage")
    options.add_argument("no-sandbox")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(service=service, options=options)
    driver.get("http://automated.pythonanywhere.com/login/")
    return driver


# To extract the temperature only
def clean_text(text):
    output = float(text.split(": ")[1])
    return output


# Extract the text and dynamic time value of the website
"""
def main():
    driver = get_driver()
    time.sleep(2)
    element = driver.find_element(by="xpath", value="/html/body/div[1]/div/h1[2]")
    # return element.text
    return clean_text(element.text)
print(main())
"""


# Automatically input login form
def main():
    driver = get_driver()
    driver.find_element(by="id", value="id_username").send_keys("automated")
    time.sleep(2)
    # return the enter key
    driver.find_element(by="id", value="id_password").send_keys("automatedautomated" + Keys.RETURN)
    driver.find_element(by="xpath", value="/html/body/nav/div/a").click()
    print(driver.current_url)
    time.sleep(2)
    temp_element = driver.find_element(by="xpath", value="/html/body/div[1]/div/h1[2]")
    print(clean_text(temp_element.text))
    time.sleep(5)
    driver.close()


print(main())