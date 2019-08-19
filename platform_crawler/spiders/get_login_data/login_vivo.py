"""
version 1:
    index:get sessionid, k,tk, captcha:update k, tk;  post: vc, un, pwd   + cookies
version 2:
    use chrome driver
"""
import time
import json
import logging
import pyautogui as pag
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from platform_crawler.utils.post_get import get
from platform_crawler.utils.utils import Util
from platform_crawler.spiders.pylib.post_res import post_res
from platform_crawler import settings


u = Util()
logger = None


class LocationError(Exception):

    def __init__(self, err_info):
        self.err_info = err_info
        super().__init__(self)

    def __str__(self):
        return self.err_info


class Vivo:

    def __init__(self, user_info, log_name):
        global logger
        self.d = None
        self.acc = user_info.get('account')
        self.pwd = user_info.get('password')
        self.user_info = user_info
        self.wait = None
        logger = logging.getLogger(log_name)

    def init_driver(self):
        driver = webdriver.Chrome()
        driver.set_page_load_timeout(60)        # 页面超时时间
        driver.set_script_timeout(60)           # js加载超时时间
        driver.maximize_window()
        return driver

    def get(self, url):
        for e in range(5):
            try:
                self.d.delete_all_cookies()
                self.d.get(url)
                time.sleep(3)
                break
            except: # 超时重试一次
                time.sleep(3)
                continue

    def wait_element(self, element_type, wait_sth):
        ele = self.wait.until(EC.presence_of_element_located((element_type, wait_sth)))
        return ele

    def get_vc(self):
        vc_path = settings.join(settings.IMG_PATH, 'vc.png')
        im = None
        try:
            element = self.d.find_element_by_xpath('//*[@id="frm-login"]//img')
            if u.cutimg_by_driver(self.d, element, vc_path):
                with open(vc_path, 'br') as i:
                    im = i.read()
            vc_res = u.rc.rk_create(im, 3040)
            verify_code = vc_res.get('Result').lower()
            return verify_code, vc_res, im
        except:
            return self.get_vc()

    def is_login(self, data):
        cookie = '; '.join(['%s=%s' % (e['name'], e['value']) for e in data])
        url = 'https://dev.vivo.com.cn/webapi/user/info?timestamp=%s' % int(time.time()*1000)
        haeders = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Content-Type': 'application/json;charset=UTF-8',
            'Cookie': cookie,
            'Host': 'dev.vivo.com.cn',
            'Origin': 'https://dev.vivo.com.cn',
            'Referer': 'https://dev.vivo.com.cn/home',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
        }
        res = get(url, headers=haeders, timeout=10)
        if not res.get('is_success'):
            raise Exception(res.get('msg'))
        res = json.loads(res.get('msg').content)
        if res.get('code') != 0:
            logger.info('login failed')
            return {'succ': False, 'msg': 'login failed'}
        logger.info('login success')
        return {'succ': True, 'msg': 'login success'}

    def login(self, retrytimes=0):
        try:
            url = 'http://id.vivo.com.cn'
            self.get(url)
            self.wait_element(By.NAME, 'name').clear()
            self.wait_element(By.NAME, 'name').send_keys(self.acc)
            self.wait_element(By.NAME, 'password').clear()
            self.wait_element(By.NAME, 'password').send_keys(self.pwd)
            verify_code, vc_obj, img = self.get_vc()
            self.wait_element(By.XPATH, '//input[@data-bv-field="verificationCode"]').send_keys(verify_code)
            self.d.find_element_by_class_name('frm-action').click()
            time.sleep(5)
            pag.hotkey('esc', interval=0.3)
            pag.hotkey('ctrl', 'r', interval=0.3)
            cookies = self.d.get_cookies()
            login_res = self.is_login(cookies)
            if not login_res.get('succ'):
                u.rc.rk_report_error(vc_obj.get('Id'))
                if retrytimes > 4:
                    self.d.quit()
                    return {'succ': False, 'msg': 'login failed after 5 times', 'desc': 'account: %s----pd: %s' % (self.acc, self.pwd)}
                retrytimes += 1
                return self.login(retrytimes=retrytimes)
            try:
                self.d.implicitly_wait(5)
                self.d.execute_script('document.querySelector("button.btn-border").click()')
            except:
                pass
            u.rc.rk_report(img, 3040, verify_code, vc_type=self.user_info.get('platform'))
            return {'succ': True, 'cookies': cookies, 'driver': self.d}
        except Exception as er:
            logger.error(er, exc_info=1)
            self.d.quit()
            return {'succ': False, 'msg': 'got an exception with unknown reason'}

    def run_login(self):
        self.d = self.init_driver()
        self.wait = WebDriverWait(self.d, 20)
        res = self.login()
        if not res.get('succ'):
            # post_res(self.user_info.get('id'), self.acc, self.user_info.get('platform'), None, False)
            logger.error('login failed, post res success')
            res['invalid_account'] = True
        return res
