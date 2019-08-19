import requests
from selenium import webdriver
import time

driver = webdriver.Chrome()
session_requests = requests.session()
driver.maximize_window()

login_url = "http://118.178.90.232/web/login.jsp"

driver.get(login_url)

vercode = driver.find_element_by_xpath("//span[@class='add phoKey']").text
elem_user = driver.find_element_by_xpath('//input[@id="name"]')
elem_user.send_keys('lszh')
time.sleep(1)
elem_pwd = driver.find_element_by_xpath('//input[@id="passwd"]')
elem_pwd.send_keys('lszh001')
time.sleep(1)
elem_ver = driver.find_element_by_xpath('//input[@class="sradd photokey"]')
elem_ver.send_keys(vercode)
time.sleep(1)

driver.find_element_by_xpath("//div[@class='sub']/button").click()
time.sleep(3)


driver.find_element_by_link_text('学员培训过程管理').click()
time.sleep(2)
driver.find_element_by_id('100041_100054').click()
time.sleep(3)
driver.switch_to.frame(driver.find_element_by_id('Frame_tab_100041_100054'))
time.sleep(2)
driver.find_element_by_id('moreselect').click()     # 到高级查询了，你后面自己试着做吧，我还有7个登陆平台要写
time.sleep(60*1)


