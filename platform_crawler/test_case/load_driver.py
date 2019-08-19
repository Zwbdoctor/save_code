from selenium.webdriver import Chrome
import time


url = 'https://developer.huawei.com/consumer/cn/service/apcs/app/home.html'
ck = 'apppromote_lang=cn; APCS_AT="CFwH17cENO7L4jUd/y7MlRsHFBzkKRUjo8iCuQtgoNlRvUPthwzltcQTH+4mZ0fCPSFCRFk+s4SwszZ9RoTH5//Upk96HCea9DrxHLarEOc5gYVlXtw="; SITE_ID=1'
ck = [{'name': x.split('=')[0], 'value': x.split('=')[1]} for x in ck.split('; ')]
d = Chrome()
d.get(url)
for c in ck:
    d.add_cookie(c)

d.get(url)
time.sleep(60)