from excel_parser import read_tokens, write_result
from fake_useragent import UserAgent
from selenium.common import WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from functools import partial
from locators import *
from userdata_handler import get_user_data
from log import get_logger
from multiprocessing import Pool

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
    wait = WebDriverWait(driver, 100)
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

        if is_element_present(driver, wait, EMAIL_ERROR):
            handle_login_error("Login error")

        # logger.info("Email passed")

        wait.until(EC.element_to_be_clickable(PASSWORD_FIELD)).send_keys(password)
        wait.until(EC.element_to_be_clickable(NEXT_BUTTON)).click()

        if is_element_present(driver, wait, PASSWORD_ERROR):
            handle_login_error("Password error")

        # logger.info("Password passed")
        wait.until(EC.element_to_be_clickable(NEXT_BUTTON)).click()
        # logger.info("Authentication passed")

        try:
            frame = WebDriverWait(driver, 100).until(lambda _: driver.find_element(*FRAME))
            driver.switch_to.frame(frame)
        except:
            logger.error("Not switch frame")

    except WebDriverException as e:
        # logger.error(f"Selenium WebDriverException: {e}")
        handle_login_error("Unexpected error during authentication")


def is_element_present(driver, wait, locator):
    try:
        wait.until(driver.find_element(*locator))
        return True
    except:
        return False


def handle_login_error(error_message):
    # logger.error(error_message)
    raise AuthenticationError(error_message)


class AuthenticationError(Exception):
    pass


def check_token(driver, wait, token):
    # Token validity check
    try:
        wait.until(EC.visibility_of_element_located(TOKEN_FIELD))

        token_field = driver.find_element(*TOKEN_FIELD)
        token_field.clear()
        token_field.send_keys(token)
    except:
        logger.error("Not find token field")

    # logger.info("Check token")
    try:
        WebDriverWait(driver, 2).until(EC.visibility_of_element_located(FLAG))
        logger.info(f"Token {token} is invalid")
        result = {token: "invalid"}
    except:
        logger.info(f"Token {token} is valid")
        result = {token: "valid"}

    return result


def check_tokens(driver, wait, tokens: list):
    results_dict = {}
    for token in tokens:
        results_dict.update(check_token(driver, wait, token))
    return results_dict


def start_single_check(token, data):
    driver, wait = get_webdriver()
    result = {token, None}
    try:
        authenticate(driver, wait, data)
        result = check_token(driver, wait, token)
    except Exception as e:
        logger.error(f"Script execution failed: {e}")
    finally:
        driver.close()
        driver.quit()

    return result


def multiple_check(data, tokens):
    try:
        driver, wait = get_webdriver()

        authenticate(driver, wait, data)
        result_dict = check_tokens(driver, wait, tokens)
        return result_dict
    except Exception as e:
        logger.error(f"Script execution failed: {e}")


def start_pool_check(data_path: str, data, filename):
    try:
        tokens = read_tokens(file_path=data_path)
        result_check = {}

        chunk_size = 40
        chunks = [tokens[i:i + chunk_size] for i in range(0, len(tokens), chunk_size)]

        if len(chunks) > 1:
            p = Pool(processes=len(chunks) if len(chunks) < 4 else 4)
            partial_multiple_check = partial(multiple_check, data)
            for chunk_result in p.map(partial_multiple_check, chunks):
                result_check.update(chunk_result)
        else:
            result_check = multiple_check(data, chunks[0])

        write_result(filename, result_check)
    except Exception as e:
        logger.error(f"Script execution failed: {e}")


if __name__ == "__main__":
    start_pool_check("/home/gw1xo/Стільниця/TestAeon/tokens.xlsx",
                     get_user_data("/home/gw1xo/Стільниця/TestAeon/userdata/Gw1xo_auth.json"),
                     "test")
