import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import threading
import time
import datetime
from cli import read_user_cli, _get_website_urls

service = Service('/Users/hhvn/Downloads/chromedriver')


def get_driver(urls):
    options = webdriver.ChromeOptions()
    options.add_argument("disable-infobars")
    options.add_argument("start-optimized")
    options.add_argument("disable-dev-shm-usage")
    options.add_argument("no-sandbox")
    options.add_argument("start-optimized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(service=service, options=options)
    for url in urls:
        driver.get(url)
        return driver


def get_temperature(element_text):
    temp = float(element_text.split(": ")[1])
    return temp


def get_datetime():
    output = datetime.datetime.utcnow().strftime('%d-%m-%Y-%H:%M:%S')
    return output


def clean_text(element_text):
    output = float(element_text.split(": ")[1])
    return output


def _web_crawling(urls):
    threading.Timer(10.0, main).start()
    title = get_datetime()
    with open(f"scrape_data/{title}.txt", "w") as file:
        driver = get_driver(urls)
        driver.find_element(by="id", value="id_username").send_keys("automated")
        time.sleep(3)
        driver.find_element(by="id", value="id_password").send_keys("automatedautomated" + Keys.RETURN)
        driver.find_element(by="xpath", value="/html/body/nav/div/a").click()
        print(driver.current_url)
        time.sleep(3)
        element = driver.find_element(by="xpath", value="/html/body/div[1]/div/h1[2]")
        print(clean_text(element.text))
        time.sleep(10)
        driver.quit()


def main():
    user_args = read_user_cli()
    urls = _get_website_urls(user_args)
    if not user_args:
        print('Enter urls!', file=sys.stderr)
        sys.exit(1)
    else:
        _web_crawling(urls)


if __name__ == '__main__':
    print(main())