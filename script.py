import os
from time import sleep
from fake_useragent import UserAgent
from selenium.common import WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from locators import *
from log import get_logger
import sys

URL = "https://account.microsoft.com/billing/redeem?ref=xboxcom"

# Set up logging
logger = get_logger()

def get_webdriver():
    # user_agent
    useragent = UserAgent()

    # options
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={useragent.random}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless")

    # driver
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        logger.error(f"Error initializing WebDriver: {e}")
        raise

    # wait
    wait = WebDriverWait(driver, 20)
    return driver, wait


def authenticate(driver, wait, email: str, password: str):
    try:
        driver.get(URL)

        # Passing authentication
        logger.info("Passing authentication...")
        wait.until(EC.element_to_be_clickable(EMAIL_FIELD)).send_keys(email)
        wait.until(EC.element_to_be_clickable(NEXT_BUTTON)).click()

        sleep(2)
        if is_element_present(driver, EMAIL_ERROR):
            handle_login_error("Login error")

        logger.info("Email passed")

        wait.until(EC.element_to_be_clickable(PASSWORD_FIELD)).send_keys(password)
        wait.until(EC.element_to_be_clickable(NEXT_BUTTON)).click()

        sleep(2)
        if is_element_present(driver, PASSWORD_ERROR):
            handle_login_error("Password error")

        logger.info("Password passed")
        wait.until(EC.element_to_be_clickable(NEXT_BUTTON)).click()
        logger.info("Authentication passed")
    except WebDriverException as e:
        logger.error(f"Selenium WebDriverException: {e}")
        handle_login_error("Unexpected error during authentication")


def is_element_present(driver, locator):
    try:
        return bool(driver.find_element(*locator))
    except:
        return False


def handle_login_error(error_message):
    logger.error(error_message)
    raise AuthenticationError(error_message)


class AuthenticationError(Exception):
    pass


def check_token(driver, wait,token: str):
    try:
        sleep(10)
        frames = driver.find_elements(*FRAMES)
        driver.switch_to.frame(frames[0])

        # Token validity check
        element = wait.until(EC.presence_of_element_located(TOKEN_FIELD))
        element.send_keys(token)

        logger.info("Check token")
        sleep(4)
        flag = wait.until(EC.presence_of_element_located(FLAG_BUTTON))
        if flag.is_enabled():
            logger.info(f"Token {token} is valid")
        else:
            logger.info(f"Token {token} is invalid")
    except Exception as e:
        logger.error(f"Error during token check: {e}")
        sys.exit(1)
    finally:
        driver.close()
        driver.quit()


def start_check(token, email, password):
    try:
        driver, wait = get_webdriver()
        authenticate(driver, wait, email, password)
        check_token(driver, wait, token)
    except Exception as e:
        logger.error(f"Script execution failed: {e}")
