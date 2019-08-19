'''
login qq common -- http://e.qq.com zwb
'''
from platform_crawler.spiders.pylib.post_res import post_res
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from platform_crawler.spiders.get_login_data.login_qq_common import LoginQQCommon

import logging

logger = None


class LoginQQ(LoginQQCommon):
    def __init__(self, user_info):
        global logger
        logger = logging.getLogger('%s.login_qq' % user_info.get('platform'))
        self.user_info = user_info.copy()
        self.d = None
        self.wait = None
        user_info['platform'] = '%s.login_qq_common' % user_info.get('platform')
        super().__init__(user_info)

    def initDriver(self):
        self.d = webdriver.Chrome()
        self.d.set_page_load_timeout(60)
        self.d.set_script_timeout(30)
        self.d.maximize_window()

    def waitElement(self, element_type, wait_sth):
        self.wait = WebDriverWait(self.d, 20)
        ele = self.wait.until(EC.visibility_of_element_located((element_type, wait_sth)))
        return ele

    def click_to_login(self):
        self.d.get('https://e.qq.com')
        headerLoginBtn = self.waitElement(By.ID, 'loginBtn')
        headerLoginBtn.click()
        loginIfr = self.waitElement(By.CSS_SELECTOR, 'iframe[id="ptlogin_iframe"]')
        return loginIfr

    # 登录重试
    def run_login(self):
        res = None
        for e in range(1, 6):
            self.initDriver()
            loginIfr = self.click_to_login()
            res = self.login(driver=self.d, loginIfr=loginIfr)
            if res['succ']:
                self.d.quit()
                return res
            else:
                self.d.quit()
        else:
            # 上报无效
            # params = [self.user_info.get('id'), self.user_info.get('account'), self.user_info.get('platform'), None, False]
            # if not post_res(*params):
            #     logger.error('----------useless account! Post result failed!')
            # else:
            logger.info('useless account!(%s) Post success!' % self.user_info.get('account'))
            self.d.quit()
            return {'succ': False, 'msg': res.get('msg')}


