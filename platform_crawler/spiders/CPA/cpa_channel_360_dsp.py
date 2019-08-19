'''
cpa http://channel.360.cn/ zly
截图位置和子账号不同，需要截到渠道号
'''
from platform_crawler.utils.utils import Util

from selenium.webdriver.common.by import By
import time
from platform_crawler.spiders.CPA.cpa_channel_360_zong import Channel360zong
from platform_crawler.settings import join, IMG_PATH

u = Util()


# 360子账号任务类
class Cpa360Dsp(Channel360zong):
    def __init__(self, data, **kwargs):
        print('360子账号任务类初始化')
        super().__init__(data, **kwargs)

    # 重写登录框逻辑
    def login(self, ui):
        self.d.get('http://channel.360.cn/')
        self.d.implicitly_wait(10)
        loginBtn = self.wait_element(By.CSS_SELECTOR, '._1wpszmp05gC2wm2vtV-s3d>div a:first-child')
        loginBtn.click()
        inpUser = self.wait_element(By.CSS_SELECTOR, 'input[name="username"]')
        inpUser.clear()
        inpUser.send_keys(ui['account'])
        inpPass = self.d.find_element_by_css_selector('input[name="password"]')
        inpPass.clear()
        inpPass.send_keys(ui['password'])
        time.sleep(1)

        vcimgpath = join(IMG_PATH, 'app_imgs', 'channel360SonVerifyCode.png')
        vcodeimg = self.d.find_element_by_css_selector('._1wSO9-qM_eUcUq8JnAeHkD img')
        u.cutimg_by_driver(self.d, vcodeimg, vcimgpath)
        with open(vcimgpath, 'rb') as f:
            im = f.read()
        lkres = u.rc.rk_create(im, '3040')
        lk, lk_id = lkres.get('Result'), lkres.get('Id')
        inpVc = self.d.find_element_by_css_selector('input[name="validate"]')
        inpVc.send_keys(lk)
        time.sleep(2)

        btnLogin = self.d.find_element_by_css_selector('button[type="submit"]')
        btnLogin.click()
        time.sleep(4)

        loginRes = self.isLogin()
        self.logger.info('isLogin:%s' % loginRes)
        if loginRes == False:
            try:
                text = self.d.find_element_by_css_selector('.form-group span').text
                if text == '验证码错误':
                    u.rc.rk_report_error(lk_id.get('Id'))
            finally:
                return {'succ': False, 'msg': 'login fail'}
        else:
            u.rc.rk_report(im, 3040, lk, vc_type=ui.get('platform'))
            return {'succ': True, 'cookies': self.d.get_cookies(), 'appdict': loginRes}
