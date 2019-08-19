import logging
import time
import json

from platform_crawler.utils.utils import Util
from platform_crawler.utils.post_get import post
from platform_crawler.settings import IMG_PATH, join
from platform_crawler.spiders.get_login_data.BaseModel import Base

u = Util()
logger = None


class Huawei(Base):

    def __init__(self, user_info, log_name):
        global logger
        self.d = None
        self.acc = user_info.get('account') if user_info.get('account') != 'dlr@btomorrow.cn' else 'larqinh@163.com'
        self.pwd = user_info.get('password') if user_info.get('account') != 'dlr@btomorrow.cn' else 'Hhmt123456'
        self.user_info = user_info
        logger = logging.getLogger('%s.login' % log_name)
        super().__init__()

    def get(self, url):
        try:
            self.d.get(url)
        except:     # 超时重试一次
            self.d.get(url)
        self.d.implicitly_wait(5)
        time.sleep(3)

    def deal_vc(self):
        # 裁剪
        element = self.d.find_element_by_id('token-img')
        img_path = join(IMG_PATH, 'vc.png')
        u.cutimg_by_driver(self.d, element, img_path)
        with open(img_path, 'br') as i:
            img = i.read()

        vc = u.rc.rk_create(img, 3040)['Result'].lower()
        # 验证
        self.d.find_element_by_id('uc-common-token').send_keys(vc)
        self.d.find_element_by_id('submit-form').click()
        time.sleep(2)
        # res = self.is_login(check_cookie)
        try:
            self.d.find_element_by_class_name('logout')
            return {'succ': True, 'msg': 'login success'}
        except:
            logger.info('no logout btn, mean not login, pass to vc_pwd step')
            vc_res = self.d.find_element_by_id('token-error').text
            pwd_res = self.d.find_element_by_id('account-error').text
            if vc_res == '验证码错误':
                return {'succ': False, 'msg': 'vc'}
            if pwd_res == '用户名密码错误':
                return {'succ': False, 'msg': 'pd'}

    def is_login(self, cookie):
        url = 'https://developer.huawei.com/consumer/cn/service/apcs/app/gwService'
        cookie = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in cookie])
        headers = {
            'accept': "application/json, text/javascript, */*; q=0.01",
            'Content-Type': "application/json",
            'cookie': cookie,
            'origin': "https://developer.huawei.com",
            'referer': "https://developer.huawei.com/consumer/cn/service/apcs/app/home.html",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        }
        data = {
            'apiName': 'OpenUP.Developer.getInfo',
            'params': '{"queryRangeFlag":"000110"}'
        }
        res = post(url, data=json.dumps(data), headers=headers)
        if not res.get('is_success'):       # 网络异常
            return {'succ': False, 'msg': res.get('msg')}
        data = json.loads(res.get('msg').content)
        # logger.info(data)
        if data.get('retCode') == 0:
            return {'succ': True, 'msg': 'login success'}
        else:           # 登陆失败
            return {'succ': False, 'msg': 'login failed'}

    def login(self, retrytimes=0):
        self.init_driver_with_real_chrome(self.user_info.get('platform'))
        url = 'https://developer.huawei.com/consumer/cn/service/apcs/app/home.html'
        try:
            self.get(url)
            self.d.find_element_by_id('hw_index_login').click()
            time.sleep(2)
            self.d.find_element_by_id('login_userName').send_keys(self.acc)
            self.d.find_element_by_id('login_userName').clear()
            self.d.find_element_by_id('login_userName').send_keys(self.acc)
            time.sleep(2)
            self.d.execute_script('document.querySelector("#login_password").value="%s"' % self.pwd)
            # self.d.find_element_by_id('login_password').clear()
            # self.d.find_element_by_id('login_password').send_keys(self.pwd)
            # input('-------------输入完成以后，请回车继续----------------')
            self.d.find_element_by_id('btnLogin').click()
            time.sleep(2)
            # login_res = self.deal_vc()    # 处理验证码和判断登陆结果
            check_cookie = self.d.get_cookies()
            login_res = self.is_login(check_cookie)
            if not login_res.get('succ'):
                self.close_chrome_debugger(delete_user_data=True)
                if login_res.get('msg') == 'vc':
                    time.sleep(1)
                    return self.login(retrytimes=retrytimes)
                elif login_res.get('msg') == 'pd':
                    if retrytimes == 5:
                        return login_res
                    retrytimes += 1
                    time.sleep(1)
                    return self.login(retrytimes=retrytimes)
            cookies = self.d.get_cookies()
            return {'succ': True, 'cookies': cookies, 'driver': self.d}
        except Exception as e:
            logger.error(e, exc_info=1)
            self.close_chrome_debugger(delete_user_data=True)
            if retrytimes == 5:
                return {'succ': False, 'msg': e}
            retrytimes += 1
            time.sleep(1)
            return self.login(retrytimes=retrytimes)

    def run_login(self):
        res = self.login()

        if not res.get('succ'):
            # params = [self.user_info.get('id'), self.acc, self.user_info.get('platform'), None, False]
            # if not post_res(*params):
            #     logger.error('login failed, post failed, account: %s' % self.acc)
            logger.info('login failed, post success')
            res['invalid_account'] = True
        return res

