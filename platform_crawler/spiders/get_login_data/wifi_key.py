import time
import logging
from requests import get
from platform_crawler.utils.utils import Util
from platform_crawler.spiders.get_login_data.BaseModel import Base
from platform_crawler.settings import BASEDIR, join

logger = None
u = Util()


class WifiKey(Base):

    def __init__(self, user_info, log_name, *args, **kwargs):
        global logger
        self.d = None
        self.acc = user_info.get('account')
        self.pwd = user_info.get('password')
        self.user_info = user_info
        self.ua = None
        logger = logging.getLogger(log_name)
        super().__init__(*args, **kwargs)

    def get_verify_wifi(self, c):
        url = 'http://ad.wkanx.com/user/captcha',
        params = {'t': int(time.time())},
        headers = {
            'Host': 'ad.wkanx.com', 'Referer': 'http://ad.wkanx.com/',
            'Cookie': 'laravel_session=%s' % c['value'],
            'User-Agent': self.ua}
        img = get(url, params=params, headers=headers, timeout=60)
        verify_code = u.rc.rk_create(img.content, 3040)
        self.d.delete_cookie('laravel_session')
        c['value'] = img.cookies.get('laravel_session')
        c.pop('expiry')
        self.d.add_cookie(c)
        return verify_code, img.content

    def get_verify_img(self):
        captcha = self.d.find_element_by_css_selector('.captcha img')
        imgpath = join(BASEDIR, 'imgs', 'wifi_imgs', 'verify.png')
        u.cutimg_by_driver(self.d, captcha, imgpath)
        with open(imgpath, 'br') as i:
            img = i.read()
        captcha_code = u.rc.rk_create(img, 3040)
        return captcha_code, img

    def deal_vc_res(self):
        # 获取验证码图片
        # verify_code, im = self.get_verify_wifi(cookie, **param_list)
        verify_code, im = self.get_verify_img()
        self.d.find_element_by_name('verifyCode').send_keys(verify_code.get('Result').lower())
        time.sleep(1)
        self.d.find_element_by_xpath('//form[@name="form"]//button[@type="submit"]').click()
        self.d.implicitly_wait(5)
        try:
            res_text = self.d.find_element_by_css_selector('div.ng-binding').text
            if res_text == '验证码不正确':
                u.rc.rk_report_error(verify_code.get('Id'))
                return {'succ': False, 'msg': 'vc'}
            elif res_text == '用户名或密码不正确':
                return {'succ': False, 'msg': 'pwd'}
        except:
            pass
        time.sleep(2)
        self.d.implicitly_wait(1)
        try:
            self.d.find_element_by_id('ngdialog3-aria-labelledby')
            raise Exception('unkown error: sth covered in the page')
        except:
            u.rc.rk_report(im, 3040, verify_code.get('Result').lower(), vc_type=self.user_info.get('platform'))
            return {'succ': True}

    def init_browser_and_page(self):
        self.d = self.init_driver_with_real_chrome(self.user_info.get('platform'))
        self.ua = self.d.execute_script('return window.navigator.userAgent')
        url = 'http://ad.wkanx.com/#/user/login'
        self.d.get(url)
        self.d.delete_all_cookies()
        self.d.refresh()

    def login(self):
        self.d.find_element_by_name('email').send_keys(self.acc)
        self.d.find_element_by_name('password').send_keys(self.pwd)
        c = self.d.get_cookie('laravel_session')

        login_res = self.deal_vc_res(c)
        if not login_res.get('succ') and login_res.get('msg') == 'vc':
            self.d.refresh()
            logger.info('verify failed')
            return login_res
        elif not login_res.get('succ') and login_res.get('msg') == 'pwd':
            login_res['msg'] = 'account error'
            logger.info('account error')
            return login_res
        try:  # 处理登陆后  账号的其他异常
            self.d.find_element_by_id('ngdialog2-aria-labelledby')
            logger.info('账号异常')
            self.close_chrome_debugger()
            raise Exception('unkown error: after login sucess')
        except:
            pass

        cookies = self.d.get_cookies()
        return {'succ': True, 'cookie': cookies, 'driver': self.d}

    def login_(self, vc_times=1, pwd_times=1, refresh_times=0):
        url = 'http://ad.wkanx.com/#/user/login'
        self.d.get(url)
        try:
            self.d.find_element_by_link_text('退出').click()
        except:
            pass
        self.d.implicitly_wait(3)
        try:  # 第一次get页面刷新失败
            self.d.find_element_by_css_selector('.sems-login-form')
        except:
            refresh_times += 1
            if refresh_times == 10:
                return {'succ': False, 'msg': 'login page got failed, please check the login page'}
            return self.login_(vc_times=vc_times, pwd_times=pwd_times, refresh_times=refresh_times)
        try:
            self.d.find_element_by_name('email').send_keys(self.acc)
            self.d.find_element_by_name('password').send_keys(self.pwd)
            c = self.d.get_cookie('laravel_session')

            login_res = self.deal_vc_res()
            if not login_res.get('succ') and login_res.get('msg') == 'vc':
                self.d.refresh()
                if vc_times >= 5:
                    return {'succ': False}
                vc_times += 1
                return self.login_(vc_times=vc_times, pwd_times=pwd_times)
            elif not login_res.get('succ') and login_res.get('msg') == 'pwd':
                self.d.refresh()
                if pwd_times >= 3:
                    return {'succ': False, 'msg': 'account error'}
                pwd_times += 1
                return self.login_(vc_times=vc_times, pwd_times=pwd_times)
            elif not login_res.get('succ'):
                return {'succ': False}
            try:  # 处理登陆后  账号的其他异常
                self.d.find_element_by_id('ngdialog2-aria-labelledby')
                logger.info('账号异常')
                self.d.quit()
                return {'succ': False}
            except:
                pass

            cookies = self.d.get_cookies()
            return {'succ': True, 'cookie': cookies, 'driver': self.d}
        except Exception as e:
            logger.error(e, exc_info=1)
            self.d.quit()
            return {'succ': False}

    def run_login(self):
        self.init_browser_and_page()
        for x in range(3):
            res = self.login_()
            if res.get('succ'):
                return res
            elif res.get('msg') == 'account error':
                logger.info('login failed, ready to post res')
                self.d.quit()
                res['invalid_account'] = True
                return res
