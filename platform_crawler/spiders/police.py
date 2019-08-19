from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions


co = ChromeOptions()
co.add_argument('--headless')
d = Chrome(options=co)


def wait_element(element_type, text, wait_time=10):
    wait = WebDriverWait(d, wait_time)
    if wait_time != 10:
        wait._timeout = wait_time
    element = wait.until(EC.presence_of_element_located((element_type, text)))
    return element


def login():
    url = 'https://bj.122.gov.cn/m/login'
    d.get(url)
    wait_element(By.ID, 'csessionid').click()
    el = wait_element(By.CSS_SELECTOR, 'div.controls span.valcode img')
    src = el.get_attribute('src')
    print(src)
    d.quit()


if __name__ == '__main__':
    login()
