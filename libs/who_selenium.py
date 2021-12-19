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

SCREENSHOT_PATH = os.getenv("SCREENSHOT_PATH", "/tmp/pic.png")


def get_who_covid_information(options):
    """Open website, click Sign in, input login/pass and check if dashboard is open."""

    # defaults
    result = {"status": False, "ellapsed_time": 100, "info": "N/A"}
    url = options.get("url")

    try:
        logging.info(f"Open {url}")

        # Create instance
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--ignore-ssl-errors=yes")
        options.add_argument("--ignore-certificate-errors")
        driver = webdriver.Chrome(options=options)

        # Open WHO main page
        driver.get(url)
        start = datetime.now()
        time.sleep(5)
        element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="PageContent_C440_Col00"]/article/main/div/a')
            )
        )

        # Click on the "All info here" button
        element.click()

        # Wait till the "Numbers at a glance" div will be available and parse confirmed deaths and cases from HTTP code.
        confirmed_cases_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "confirmedCases"))
        )
        confirmdes_death_element = driver(By.ID, 'confirmedDeaths')

        # Get numbers
        confirmed_cases = int(confirmed_cases_element.text.replace(" ", ""))
        confirmed_deaths = int(confirmdes_death_element.text.replace(" ", ""))

        # Return results
        result = {
            "ellapsed_time": (datetime.now() - start).seconds,
            "confirmed_cases": confirmed_cases,
            "confirmed_deaths": confirmed_deaths
        }

        logging.info("Success. result: %s. \n Screenshot saved in %s", str(result), SCREENSHOT_PATH)
    except Exception as exception:
        logging.error("Failed with exception. Screenshot saved in %s. %s", SCREENSHOT_PATH, str(exception))
    finally:
        driver.save_screenshot(SCREENSHOT_PATH)
        driver.quit()


if __name__ == "__main__":
    options = {"url": "https://www.who.int/home"}
    get_who_covid_information(options)
