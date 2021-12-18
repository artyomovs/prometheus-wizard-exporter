""" Check frontend with selenium driver. """

import logging
import os
import time

from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.getLogger().setLevel(logging.INFO)
logging.getLogger("selenium.webdriver.remote.remote_connection").setLevel(logging.WARNING)

URL = os.getenv("URL", "https://localhost/auth/login")
SCREENSHOT_PATH = os.getenv("SCREENSHOT_PATH", "/tmp/pic.png")
USERNAME = os.getenv("USERNAME", None)
PASSWORD = os.getenv("PASSWORD", None)


def check_website_signin():
    """Open website, click Sign in, input login/pass and check if dashboard is open."""

    # defaults
    result = {"status": False, "ellapsed_time": 100, "info": "N/A"}

    if not (USERNAME or PASSWORD):
        result["info"] = "Env USERNAME or PASSWORD not defined. Exit."
    else:
        try:
            logging.info("Sign in...")
            # Create instance
            options = webdriver.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--ignore-ssl-errors=yes")
            options.add_argument("--ignore-certificate-errors")
            driver = webdriver.Chrome(options=options)

            # Sign in and parse results
            driver.get(URL)
            start = datetime.now()
            element = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="root"]/div/div[1]/div/div[2]/button/span')
                )
            )
            element.click()
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "Login"))
            )
            driver.find_element(By.NAME, "Login").send_keys(USERNAME)
            driver.find_element(By.NAME, "Password").send_keys(PASSWORD)
            driver.find_element(
                By.XPATH, '//*[@id="root"]/div/div/span'
            ).click()
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, '//*[@id="root"]/div/h1')
                )
            )
            title = driver.find_element(
                By.XPATH, '//*[@id="root"]/div/main//h1'
            ).text

            # Output
            result["ellapsed_time"] = (datetime.now() - start).seconds
            result["status"] = True
            result["info"] = f"Success. Title: {title}"

            logging.info(str(result))
        except Exception as exception:
            result["status"] = False
            result["info"] = f"Failed with exception. Screenshot saved in{SCREENSHOT_PATH}. {str(exception)}"
            logging.error(str(result))
        finally:
            driver.save_screenshot(SCREENSHOT_PATH)
            driver.quit()
    return result


if __name__ == "__main__":
    while True:
        time.sleep(20)
        check_website_signin()
