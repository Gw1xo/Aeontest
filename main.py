from selenium.webdriver.common.by import By
from time import sleep
from fake_useragent import UserAgent
from auth_data import URL, EMAIL, PASSWORD
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver

EMAILFIELD = (By.ID, "i0116")
PASSWORDFIELD = (By.ID, "i0118")
NEXTBUTTON = (By.ID, "idSIButton9")
TOKENFIELD = (By.ID, 'tokenString')
FLAGBUTTON = (By.ID, 'nextButton')

# user_agent
useragent = UserAgent()

# driver
driver = webdriver.Chrome()

# wait
wait = WebDriverWait(driver, 20)

try:
    driver.get(URL)

    # wait for email field and enter email
    wait.until(EC.element_to_be_clickable(EMAILFIELD)).send_keys(EMAIL)

    # Click Next
    wait.until(EC.element_to_be_clickable(NEXTBUTTON)).click()

    # wait for password field and enter password
    wait.until(EC.element_to_be_clickable(PASSWORDFIELD)).send_keys(PASSWORD)

    # Click Login - same id?
    wait.until(EC.element_to_be_clickable(NEXTBUTTON)).click()

    driver.implicitly_wait(5)
    if bool(driver.find_elements(by=By.ID, value='idSIButton9')):
        driver.find_element(by=By.ID, value='idSIButton9').click()
    else:
        driver.find_element(by=By.ID, value='acceptButton').click()

    sleep(15)

    # Знаходження всіх фреймів на сторінці
    frames = driver.find_elements(By.TAG_NAME, "iframe")

    # Перевірка, чи є фрейми
    if len(frames) == 0:
        print("На сторінці немає фреймів.")
    else:
        print(f"На сторінці є {len(frames)} фреймів.")

    driver.switch_to.frame(frames[0])

    element = wait.until(EC.presence_of_element_located(TOKENFIELD))
    element.send_keys("3D9TY-GR6K4-FGYCP-V4YKM-TRG6Z")

    sleep(4)
    flag = wait.until(EC.presence_of_element_located(FLAGBUTTON))

    if flag.is_enabled():
        print("Valid token")
    else:
        print("Invalid token")

    sleep(20)
except Exception as ex:
    print(ex)
finally:
    driver.close()
    driver.quit()
