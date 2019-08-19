from selenium import webdriver
from selenium.webdriver.common.by import By
import logging
import time

from platform_crawler.spiders.pylib.post_res import post_res
from platform_crawler.utils.utils import Util
from platform_crawler.settings import DEFAULT_VERIFY_PATH

u = Util()
logger = None


class XiaoMI:

    def __init__(self, user_info, log_name):
        global logger
        self.d = None
        self.acc= user_info.get('account')
        self.pwd = user_info.get('password')
        self.user_info = user_info
        logger = logging.getLogger(log_name)

    def init_driver(self):
        driver = webdriver.Chrome()
        driver.set_page_load_timeout(60)
        driver.set_script_timeout(60)
        driver.maximize_window()
        return driver

    def get(self, url):
        try:
            self.d.delete_all_cookies()
            self.d.get(url)
        except: # 超时重试一次
            self.d.delete_all_cookies()
            self.d.get(url)
        time.sleep(3)

    def deal_vc(self):
        # 裁剪
        element = self.d.find_element_by_id('captcha-img')
        img_path = DEFAULT_VERIFY_PATH
        u.cutimg_by_driver(self.d, element, img_path)
        with open(img_path, 'br') as i:
            img = i.read()

        vc_obj = u.rc.rk_create(img, 3050)
        vc = vc_obj.get('Result').lower()
        # 验证
        self.d.find_element_by_id('captcha-code').send_keys(vc)
        time.sleep(1)
        self.d.find_element_by_id('login-button').click()
        self.d.implicitly_wait(3)
        time.sleep(1)
        self.d.refresh()
        # 验证结果
        res_xpath = "//form[@id='login-main-form']"
        try:
            # 没有登陆成功
            self.d.find_element_by_xpath(res_xpath)
            u.rc.rk_report_error(vc_obj.get('Id'))
            return {'succ': False, 'msg': 'login failed'}
        except:         # 登陆成功
            u.rc.rk_report(img, 3050, vc, vc_type=self.user_info.get('platform'))
            return {'succ': True}

    def login(self, retrytimes=0):
        url = 'http://e.mi.com'
        try:
            self.get(url)
            self.d.find_element_by_xpath('//div[@class="pull-right login"]/a[1]').click()
            time.sleep(2)
            self.d.find_element_by_id('username').clear()
            self.d.find_element_by_id('username').send_keys(self.acc)
            self.d.find_element_by_id('pwd').clear()
            self.d.find_element_by_id('pwd').send_keys(self.pwd)
            self.d.find_element_by_id('login-button').click()
            # 等待验证码
            if u.wait_element(self.d, (By.ID, 'captcha-code'), 5):
                res = self.deal_vc()
                if not res.get('succ'):
                    if retrytimes == 3:
                        return {'succ': False, 'msg': 'login failed after retried 3 times'}
                    retrytimes += 1
                    return self.login(retrytimes=retrytimes)
            cookies = self.d.get_cookies()
            return {'succ': True, 'cookies': cookies, 'driver': self.d}
        except Exception as e:
            logger.error(e, exc_info=1)
            return {'succ': False, 'msg': 'unknown error: %s' % e}

    def run_login(self):
        self.d = self.init_driver()
        res = self.login()

        if res and not res.get('succ'):
            # params = [self.user_info.get('id'), self.user_info.get('account'), self.user_info.get('platform'), None, False]
            # if not post_res(*params):
            #     logger.error('login failed, post failed')
            logger.info('login failed, ready to post res')
            self.d.quit()
            res['invalid_account'] = True
        return res
