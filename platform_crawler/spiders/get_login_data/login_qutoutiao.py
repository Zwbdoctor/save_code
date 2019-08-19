from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import logging

from platform_crawler.utils.utils import Util
from platform_crawler.utils.post_get import get
from platform_crawler.settings import IMG_PATH, join

u = Util()
logger = None


class QuTouTiao:

    def __init__(self, user_info, logger_name):
        global logger
        logger = logging.getLogger(logger_name)
        self.d = None
        self.acc = user_info.get('account')
        self.pwd = user_info.get('password')
        self.user_info = user_info
        self.wait = None

    def init_driver(self):
        driver = webdriver.Chrome()
        driver.set_page_load_timeout(60)
        driver.set_script_timeout(30)
        driver.maximize_window()
        self.wait = WebDriverWait(driver, 20)
        return driver

    def wait_element(self, element_type, ele, wait_time=None):
        if wait_time:
            return WebDriverWait(self.d, wait_time).until(EC.presence_of_element_located((element_type, ele)))
        return self.wait.until(EC.presence_of_element_located((element_type, ele)))

    def get(self, url):
        try:
            self.d.delete_all_cookies()
            self.d.get(url)
        except: # 超时重试一次
            self.d.delete_all_cookies()
            self.d.get(url)
        time.sleep(4)

    def deal_vc(self):
        # 裁剪
        element = self.wait_element(By.ID, 'code_image')
        img_path = join(IMG_PATH, 'vc.png')
        u.cutimg_by_driver(self.d, element, img_path, abx=10, aby=18, chx=-10, chy=-18)
        with open(img_path, 'br') as i:
            img = i.read()

        vc_res = u.rc.rk_create(img, 3040)
        vc = vc_res.get('Result').lower()
        # 验证
        self.wait_element(By.ID, 'ctrltextcode').send_keys(vc)
        self.wait_element(By.ID, 'ctrlbuttonsubmitlabel').click()
        time.sleep(2)
        check_cookie = self.d.get_cookies()
        return self.is_login(check_cookie, vc_res, img)

    def is_login(self, cookie, vc, im):
        url = 'http://adv.aiclk.com/user?version=%s' % time.strftime('%Y%m%d%H%M')
        cookie = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in cookie])
        headers = {
            'Accept': "application/json, text/javascript, */*; q=0.01",
            'Cookie': cookie,
            'Host': "adv.aiclk.com",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        }
        res = get(url, headers=headers)
        if not res.get('is_success'):       # 网络异常
            return {'succ': False, 'msg': res.get('msg')}
        data = json.loads(res.get('msg').content)
        # logger.info(data)
        if data.get('errorType') == 'NoLogin':    # 登陆失败，两个key: retdesc, retcode
            msg = self.d.find_element_by_class_name('ui-dialog-text').text
            if msg == '开户资料正在审核中':
                return {'succ': True, 'msg': msg}
            elif msg == '验证码错误':
                u.rc.rk_report_error(vc.get('Id'))
                return {'succ': False, 'msg': 'verify_code_error'}
            elif msg == '用户名或者密码错误':
                return {'succ': False, 'msg': 'account_or_password_error'}
            else:
                return {'succ': False, 'msg': data.get('message')}
        else:
            u.rc.rk_report(im, 3040, vc.get('Result'), vc_type=self.user_info.get('platform'))
            return {'succ': True, 'msg': 'login success'}

    def login(self, retrytimes=0):
        url = 'http://adv.aiclk.com'  
        try:
            self.get(url)
            for e in range(2):
                try:
                    self.wait_element(By.ID, 'ctrldialogctrldialog__DialogAlert0layer', wait_time=3)
                    self.d.execute_script('document.querySelector("#ctrldialogctrldialog__DialogAlert0layer").remove()')
                    self.d.execute_script('document.querySelector("#ctrlMask3").remove()')
                except:
                    pass
            un = self.wait_element(By.ID, 'ctrltextusername')
            un.clear()
            un.send_keys(self.acc)
            pd = self.wait_element(By.ID, 'ctrltextpassword')
            pd.clear()
            pd.send_keys(self.pwd)
            login_res = self.deal_vc()    # 处理验证码和判断登陆结果
            if not login_res.get('succ') and login_res.get('msg') == 'account_or_password_error':
                if retrytimes == 5:
                    self.d.quit()
                    return login_res
                retrytimes += 1
                time.sleep(1)
                return self.login(retrytimes=retrytimes)
            elif not login_res.get('succ') and login_res.get('msg') == 'verify_code_error':
                return self.login(retrytimes=retrytimes)
            elif login_res.get('succ') and login_res.get('msg') == '开户资料正在审核中':
                return login_res
            time.sleep(3)
            cookies = self.d.get_cookies()

            return {'succ': True, 'cookies': cookies, 'driver': self.d}
        except Exception as e:
            logger.error(e, exc_info=1)
            if retrytimes == 5:
                self.d.quit()
                return {'succ': False, 'msg': e}
            retrytimes += 1
            time.sleep(1)
            return self.login(retrytimes=retrytimes)

    def run_login(self):
        self.d = self.init_driver()
        res = self.login()

        if not res.get('succ'):
            # params = [self.user_info.get('id'), self.user_info.get('account'), self.user_info.get('platform'), None, False]
            # if not post_res(*params):
            logger.info('login failed, post success')
            res['invalid_account'] = True
        return res


