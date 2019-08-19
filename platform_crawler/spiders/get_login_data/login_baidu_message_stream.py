from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import logging
import time
import json
import os

# from platform_crawler.spiders.pylib.get_pwd import get_pwd
from platform_crawler.spiders.pylib.post_res import post_res
from platform_crawler.utils.utils import Util
from platform_crawler.utils.post_get import post
from platform_crawler.settings import IMG_PATH, join

u = Util()
logger = None


class BaiDuMessage:

    def __init__(self, user_info, log_name):
        global logger
        self.d = None
        self.wait = None
        self.acc= user_info.get('account')
        self.pwd = user_info.get('password')
        self.user_info = user_info
        logger = logging.getLogger(log_name)

    def init_driver(self):
        driver = webdriver.Chrome()
        driver.set_page_load_timeout(60)
        driver.set_script_timeout(30)
        driver.maximize_window()
        return driver

    def wait_element(self, element_type, ele):
        return self.wait.until(EC.presence_of_element_located((element_type, ele)))

    def get(self, url):
        try:
            self.d.delete_all_cookies()
            self.d.get(url)
        except: # 超时重试一次
            self.d.delete_all_cookies()
            self.d.get(url)
        time.sleep(3)

    def fill_phone_num(self):
        self.wait_element(By.ID, 'QuestionSelect')
        set_select_element_js = """
ele = document.querySelector('#QuestionSelect'); ele.value = 100000000;
var ev = document.createEvent("HTMLEvents");
ev.initEvent("change", false, true);
ele.dispatchEvent(ev);"""
        self.d.execute_script(set_select_element_js)
        self.wait_element(By.ID, 'QuestionInput').send_keys('18503013546')
        self.d.find_element_by_id('uc-sec-confirm-btn').click()

    def deal_vc(self):
        # 裁剪
        element = self.d.find_element_by_id('token-img')
        img_path = join(IMG_PATH, 'vc.png')
        u.cutimg_by_driver(self.d, element, img_path)
        with open(img_path, 'br') as i:
            img = i.read()

        vc_res = u.rc.rk_create(img, 3040)
        vc = vc_res.get('Result').lower()
        # 验证
        self.d.find_element_by_id('uc-common-token').send_keys(vc)
        self.d.find_element_by_id('submit-form').click()
        self.d.implicitly_wait(20)
        time.sleep(3)

        # 针对某个账号，单独判断操作： 绑定手机验证
        if self.acc == '原生-智投9FA18KA1589':
            try:
                # self.wait_element(By.LINK_TEXT, '退出')
                self.d.find_element_by_link_text('退出')
                self.fill_phone_num()
                time.sleep(2)
            except Exception:
                logger.info('no logout btn, mean not login or has login, pass to vc_pwd step')

        # 普通账号结果判断
        try:
            # self.wait_element(By.CLASS_NAME, 'logout')
            self.d.find_element_by_class_name('logout')
            u.rc.rk_report(img, 3040, vc, vc_type=self.user_info.get('platform'))
            return {'succ': True, 'msg': 'login success'}
        except:
            logger.info('no logout btn, mean not login, pass to vc_pwd step')
            login_vc_res = self.d.find_element_by_id('token-error').text
            pwd_res = self.d.find_element_by_id('account-error').text
            if login_vc_res == '验证码错误':
                u.rc.rk_report_error(vc_res.get('Id'))
                logger.warning('verify failed, report ok')
                return {'succ': False, 'msg': 'vc'}
            if pwd_res == '用户名密码错误':
                return {'succ': False, 'msg': 'pd'}
            else:
                return {'succ': False, 'msg': 'unknown error'}

    def is_login(self, cookie):
        param = int(time.time()*1000)
        url = 'http://baitong.baidu.com/request.ajax?path=appads/GET/basicinfo&reqid=%s_0' % param
        cookie = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in cookie])
        headers = {
            'Accept': "*/*",
            'Content-Type': "application/x-www-form-urlencoded",
            'Cookie': cookie,
            'Host': "baitong.baidu.com",
            'Origin': "http://baitong.baidu.com",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        }
        data = {
            'path': 'appads/GET/basicinfo',
            'params': {},
            'eventId': '%s_0' % param
        }
        res = post(url, data=json.dumps(data), headers=headers)
        if not res.get('is_success'):       # 网络异常
            return {'succ': False, 'msg': res.get('msg')}
        data = json.loads(res.get('msg').content)
        # logger.info(data)
        if data.get('status') != 200:    # 登陆失败，两个key: retdesc, retcode
            return {'succ': False, 'msg': 'login failed'}
        else:
            return {'succ': True, 'msg': 'login success'}

    def login(self, retrytimes=0):
        url = 'https://www2.baidu.com'
        try:
            self.get(url)
            self.wait_element(By.CLASS_NAME, 'tab-log-type').click()
            self.wait_element(By.NAME, 'entered_login').clear()
            self.d.find_element_by_name('entered_login').send_keys(self.acc)
            self.d.find_element_by_id('ucsl-password-edit').clear()
            self.d.find_element_by_id('ucsl-password-edit').send_keys(self.pwd)
            login_res = self.deal_vc()    # 处理验证码和判断登陆结果
            if login_res.get('succ'):
                cookies = self.d.get_cookies()
                return {'succ': True, 'cookies': cookies, 'driver': self.d}
            elif not login_res.get('succ') and login_res.get('msg') == 'vc':
                time.sleep(1)
                return self.login(retrytimes=retrytimes)
            # elif not login_res.get('succ') and login_res.get('msg') == 'pd':
            else:
                if retrytimes == 5:
                    return login_res
                retrytimes += 1
                time.sleep(1)
                return self.login(retrytimes=retrytimes)
        except Exception as e:
            logger.error(e, exc_info=1)
            if retrytimes == 5:
                return {'succ': False, 'msg': e}
            retrytimes += 1
            time.sleep(1)
            return self.login(retrytimes=retrytimes)

    def run(self):
        self.d = self.init_driver()
        self.wait = WebDriverWait(self.d, 20)
        res = self.login()

        if not res.get('succ'):
            # params = [self.user_info.get('id'), self.acc, self.user_info.get('platform'), None, False]
            # if not post_res(*params):
            #     logger.error('login failed, post failed, account: %s' % self.acc)
            #     return res
            logger.info('login failed, post success')
            self.d.quit()
            res['invalid_account'] = True
        return res



