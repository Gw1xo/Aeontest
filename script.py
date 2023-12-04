from excel_parser import read_tokens, write_result
from time import sleep
from fake_useragent import UserAgent
from selenium.common import WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from functools import partial, reduce
from locators import *
from userdata_handler import get_user_data
from log import get_logger
from multiprocessing import Pool
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
    wait = WebDriverWait(driver, 30)
    return driver, wait


def authenticate(driver, wait, data):

    email = data.get('email', None)
    password = data.get('password', None)

    try:
        driver.get(URL)

        # Passing authentication
        # logger.info("Passing authentication...")
        wait.until(EC.element_to_be_clickable(EMAIL_FIELD)).send_keys(email)
        wait.until(EC.element_to_be_clickable(NEXT_BUTTON)).click()

        sleep(2)
        if is_element_present(driver, EMAIL_ERROR):
            handle_login_error("Login error")

        # logger.info("Email passed")

        wait.until(EC.element_to_be_clickable(PASSWORD_FIELD)).send_keys(password)
        wait.until(EC.element_to_be_clickable(NEXT_BUTTON)).click()

        sleep(2)
        if is_element_present(driver, PASSWORD_ERROR):
            handle_login_error("Password error")

        # logger.info("Password passed")
        wait.until(EC.element_to_be_clickable(NEXT_BUTTON)).click()
        # logger.info("Authentication passed")
    except WebDriverException as e:
        # logger.error(f"Selenium WebDriverException: {e}")
        handle_login_error("Unexpected error during authentication")


def is_element_present(driver, locator):
    try:
        return bool(driver.find_element(*locator))
    except:
        return False


def handle_login_error(error_message):
    # logger.error(error_message)
    raise AuthenticationError(error_message)


class AuthenticationError(Exception):
    pass


def check_token(driver, wait, token: str):
    result = {token: None}
    try:
        sleep(10)
        frames = driver.find_elements(*FRAMES)
        driver.switch_to.frame(frames[0])

        # Token validity check
        element = wait.until(EC.presence_of_element_located(TOKEN_FIELD))
        element.send_keys(token)

        # logger.info("Check token")
        sleep(4)
        flag = wait.until(EC.presence_of_element_located(FLAG_BUTTON))
        if flag.is_enabled():
            logger.info(f"Token {token} is valid")
            result = {token: "valid"}
        else:
            logger.info(f"Token {token} is invalid")
            result = {token: "invalid"}
    except Exception as e:
        logger.error(f"Error during token check: {e}")
    finally:
        driver.close()
        driver.quit()

    return result


def start_single_check(token, data):
    result = {token, None}
    try:
        driver, wait = get_webdriver()
        authenticate(driver, wait, data)
        result = check_token(driver, wait, token)
    except Exception as e:
        logger.error(f"Script execution failed: {e}")

    return result


def start_pool_check(data_path: str, data, filename):
    try:
        tokens = read_tokens(file_path=data_path)
        partial_check = partial(start_single_check, data=data)
        p = Pool(processes=len(tokens) if len(tokens) <= 50 else 50)
        results = p.map(partial_check, tokens)

        p.close()
        p.join()

        merge_results = {}
        for d in results:
            merge_results.update(d)
        write_result(filename, merge_results)
    except Exception as e:
        logger.error(f"Script execution failed: {e}")


if __name__ == "__main__":
    start_pool_check("/home/gw1xo/Стільниця/TestAeon/tokens.xlsx",
                     get_user_data("/home/gw1xo/Стільниця/TestAeon/userdata/Gw1xo_auth.json"),
                     "test")
