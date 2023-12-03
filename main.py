from time import sleep
from fake_useragent import UserAgent
from auth_data import URL, EMAIL, PASSWORD
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from locators import *


# user_agent
useragent = UserAgent()

# options
options = webdriver.ChromeOptions()
options.add_argument(f"user-agent={useragent.random}")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--headless")

# driver
driver = webdriver.Chrome(options=options)

# wait
wait = WebDriverWait(driver, 20)


try:
    driver.get(URL)

    # Passing authentication
    print("Passing authentication...")
    wait.until(EC.element_to_be_clickable(EMAIL_FIELD)).send_keys(EMAIL)
    wait.until(EC.element_to_be_clickable(NEXT_BUTTON)).click()
    wait.until(EC.element_to_be_clickable(PASSWORD_FIELD)).send_keys(PASSWORD)
    wait.until(EC.element_to_be_clickable(NEXT_BUTTON)).click()

    # The next button sometimes has different ids
    driver.implicitly_wait(5)
    if bool(driver.find_elements(*NEXT_BUTTON)):
        driver.find_element(*NEXT_BUTTON).click()
    else:
        driver.find_element(*ACCEPT_BUTTON).click()
    print("Authentication passed")

    sleep(10)
    frames = driver.find_elements(*FRAMES)
    driver.switch_to.frame(frames[0])

    # Token validity check
    element = wait.until(EC.presence_of_element_located(TOKEN_FIELD))
    element.send_keys("3D9TY-GR6K4-FGYCP-V4YKM-TRG6Z")

    print("Check token")
    sleep(4)
    flag = wait.until(EC.presence_of_element_located(FLAG_BUTTON))
    if flag.is_enabled():
        print("Token is valid")
    else:
        print("Token is invalid")

except Exception as ex:
    print(ex)
finally:
    driver.close()
    driver.quit()
