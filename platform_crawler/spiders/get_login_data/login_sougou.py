from selenium import webdriver
# from selenium.webdriver.common.by import By
import time
import json
import os
import logging

from platform_crawler.spiders.pylib.post_res import post_res
from platform_crawler.utils.utils import Util
from platform_crawler.utils.post_get import get
from platform_crawler.settings import IMG_PATH, join

u = Util()
logger = None


class SouGou:

    def __init__(self, user_info, log_name):
        global logger
        self.d = None
        self.acc = user_info.get('account')
        self.pwd = user_info.get('password')
        self.user_info = user_info
        logger = logging.getLogger(log_name)

    def init_driver(self):
        driver = webdriver.Chrome()
        driver.set_page_load_timeout(60)
        driver.set_script_timeout(30)
        driver.maximize_window()
        return driver

    def get(self, url):
        try:
            self.d.delete_all_cookies()
            self.d.get(url)
        except:  # 超时重试一次
            self.d.delete_all_cookies()
            self.d.get(url)
        time.sleep(3)

    def deal_vc(self):
        # 裁剪
        element = self.d.find_element_by_id('captcha-img')
        img_path = join(IMG_PATH, 'vc.png')
        u.cutimg_by_driver(self.d, element, img_path)
        with open(img_path, 'br') as i:
            img = i.read()

        vc_res = u.rc.rk_create(img, 3050)
        vc = vc_res.get('Result').lower()
        # 验证
        self.d.find_element_by_id('captcha-code').send_keys(vc)
        self.d.find_element_by_id('login-button').click()
        res_xpath = "//form[@id='login-main-form']//span[@class='error-con']"
        res_text = self.d.find_element_by_xpath(res_xpath).text
        if res_text == '验证码不正确':
            time.sleep(1)
            u.rc.rk_report_error(vc_res.get('Id'))
            self.deal_vc()
        elif res_text == '用户名或密码不正确':
            return {'succ': False, 'msg': 'login failed'}
        else:
            u.rc.rk_report(img, 3050, vc, vc_type=self.user_info.get('platform'))
            return {'succ': True}

    def is_login(self, cookie):
        cookie = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in cookie])
        yesterday = int(time.strftime('%d')) - 1
        day = '%s-%s' % (time.strftime('%Y-%m'), yesterday)
        url = 'http://agent.e.sogou.com/main/plot.html?start=%s&end=%s&type=2' % (day, day)
        headers = {
            'Accept': "application/json, text/javascript, */*; q=0.01",
            'Cookie': cookie,
            'Host': "agent.e.sogou.com",
            'Referer': "http://agent.e.sogou.com/main.html",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
            'Content-Type': "application/x-www-form-urlencoded"
        }
        res = get(url, headers=headers)
        if not res.get('is_success'):  # 网络异常
            return {'succ': False, 'msg': res.get('msg')}
        data = json.loads(res.get('msg').content)
        # logger.info(data)
        if 'plotList' in data.keys():  # 正常情况下，只有一个key: plotList
            return {'succ': True, 'msg': 'login succ'}
        elif data.get('retcode') == 401:  # 登陆失败，两个key: retdesc, retcode
            return {'succ': False, 'msg': data.get('retdesc')}
        else:
            return {'succ': False, 'msg': 'unknown error'}

    def login(self, retrytimes=0):
        url = 'http://agent.e.sogou.com/'
        try:
            self.get(url)
            self.d.find_element_by_class_name('loginBtn').click()
            time.sleep(1)
            self.d.find_element_by_name('user').clear()
            self.d.find_element_by_name('user').send_keys(self.acc)
            self.d.find_element_by_name('password').clear()
            self.d.find_element_by_name('password').send_keys(self.pwd)
            self.d.find_element_by_link_text('确认').click()
            time.sleep(2)
            # if u.wait_element(self.d, (By.ID, 'captcha-code'), 5):
            #     res = self.deal_vc()
            #     if not res.get('succ'):
            #         return res
            check_cookie = self.d.get_cookies()
            login_res = self.is_login(check_cookie)
            if not login_res.get('succ'):
                if retrytimes == 5:
                    return login_res
                retrytimes += 1
                return self.login(retrytimes=retrytimes)
            time.sleep(3)
            cookies = self.d.get_cookies()
            logger.info('login sucess')
            return {'succ': True, 'cookies': cookies, 'driver': self.d}
        except Exception as e:
            logger.error(e, exc_info=1)
            if retrytimes == 5:
                return {'succ': False, 'msg': e}
            retrytimes += 1
            return self.login(retrytimes=retrytimes)

    def run_login(self):
        self.d = self.init_driver()
        res = self.login()

        if not res.get('succ'):
            # params = [self.user_info.get('id'), self.acc, self.user_info.get('platform'), None, False]
            # if not post_res(*params):
            #     logger.error('login failed, post failed, account: %s' % self.acc)
            logger.info('login failed, post success')
            res['invalid_account'] = True
        return res
