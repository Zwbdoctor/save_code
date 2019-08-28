"""
信息流 最右 爬虫 ----  zwb
"""
from json import dump
from time import sleep
import json

from selenium.webdriver.support.wait import WebDriverWait
from requests import post
from json.decoder import JSONDecodeError

from platform_crawler.spiders.pylib.task_process import TaskProcess
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.utils.utils import Util
from platform_crawler.settings import join, IMG_PATH, JS_PATH


u = Util()
logger = None
base_header = {
    'Accept': "application/json, text/plain, */*",
    'Cookie': None,
    'Host': "ad.izuiyou.com",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36"
}


class LoginZuiYou:

    def __init__(self, ui):
        self.d = None
        self.wait = None
        self.user_info = ui
        self.acc, self.pwd = ui.get('account'), ui.get('password')

    def deal_vc(self):
        vc_name = join(IMG_PATH, 'vc_img.png')
        self.d.save_screenshot(vc_name)
        element = self.d.find_element_by_css_selector('.Captcha__img')
        u.cutimg_by_driver(self.d, element, vc_name)
        with open(vc_name, 'br') as f:
            im = f.read()
        res = u.rc.rk_create(im, '1060')
        vk = res.get('Result')
        return res, vk, im

    def is_login(self):
        url = 'http://ad.izuiyou.com/dspsrv/httpapi/fetch_account'
        cks = self.d.get_cookies()
        cookie = '; '.join(['%s=%s' % (x.get('name'), x.get('value')) for x in cks if x.get('name') != 'SERVERID'])
        headers = {
            'Accept': "application/json, text/plain, */*",
            'Content-Type': "application/json;charset=UTF-8",
            'Cookie': cookie,
            'Host': "ad.izuiyou.com",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
        }
        try:
            resp = post(url, data="{}", headers=headers, timeout=60)
            if resp.status_code != 200:
                logger.error(resp.text)
                return {'succ': False}
            res = resp.json()
            if res.get('ret') == 1:
                logger.info('login success, --- acc: %s' % self.acc)
                return {'succ': True, 'Cookie': cookie, 'driver': self.d}
            logger.info('login failed')
            return {'succ': False}
        except JSONDecodeError:
            return {'succ': False}
        except Exception as e:
            logger.error(e, exc_info=1)
            return {'succ': False}

    def login(self):
        for e in range(3):
            try:
                self.d.get('http://ad.izuiyou.com/login')
                break
            except:
                continue
        self.d.implicitly_wait(10)
        sleep(1)
        self.d.find_element_by_css_selector('input[type="text"]').send_keys(self.acc)
        self.d.find_element_by_css_selector('input[type="password"]').clear()
        self.d.find_element_by_css_selector('input[type="password"]').send_keys(self.pwd)
        vc_obj, vc, im = self.deal_vc()
        self.d.find_element_by_class_name('Captcha__input').send_keys(vc)
        self.d.find_element_by_css_selector('.ant-btn-primary').click()
        self.d.implicitly_wait(10)
        sleep(3)
        try:
            res = self.is_login()
            if not res.get('succ'):
                u.rc.rk_report_error(vc_obj.get('Id'))      # 验证结果上报
                return res
            u.rc.rk_report(im, 1060, vc, vc_type=self.user_info.get('platform'))
            return res
        except:
            return {'succ': False}

    def init_browser(self):
        from selenium import webdriver
        self.d = webdriver.Chrome()
        self.d.delete_all_cookies()
        self.d.set_page_load_timeout(60)
        self.d.set_script_timeout(60)
        self.d.maximize_window()
        self.wait = WebDriverWait(self.d, 20)

    def run_login(self):
        self.init_browser()
        for i in range(5):
            try:
                res = self.login()
                if res.get('succ'):
                    return res
            except Exception as er:
                logger.error(er, exc_info=1)
                continue
        else:
            # params = [self.user_info.get('id'), self.user_info.get('account'), self.user_info.get('platform'), None,
            #           False]
            # if not post_res(*params):
            #     logger.error('----------useless account! Post result failed!')
            # else:
            logger.info('useless account!(%s) Ready to post result!' % self.user_info.get('account'))
            self.d.quit()
            return {'succ': False, 'invalid_account': True}


class ZuiYouSpider(TaskProcess):

    def __init__(self, user_info, **kwargs):
        global logger
        super().__init__(headers=base_header, user_info=user_info, **kwargs)
        logger = self.logger

    def get_data(self, sd, ed):
        url = "http://ad.izuiyou.com/dspsrv/httpapi/fetch_billing_account_details"
        payload = {'app': 0, 'start_date': sd, 'end_date': ed, 'groupby': 0}
        res = self.deal_result(self.execute('POST', url, data=json.dumps(payload), verify=False), json_str=True)
        if not res.get('succ') or res.get('msg').get('ret') != 1:
            return res
        data = res.get('msg').get('data').get('list')
        if not data:
            return {'succ': True, 'msg': 'no data'}
        logger.info('month: %s~%s --- %s' % (sd, ed, data))
        return {'succ': True, 'msg': data}

    def change_date(self, sd, ed):
        with open(join(JS_PATH, 'zuiyou_date.js'), 'r', encoding='utf-8') as f:
            js = f.read()
        self.d.execute_script(js % (sd, ed))

    def get_img(self, sd, ed):
        # 报表部分
        url = f'http://ad.izuiyou.com/report'
        self.d.get(url)
        self.d.implicitly_wait(10)
        self.change_date(sd, ed)
        pic_name = f'{sd}_{ed}.png'
        height = self.d.execute_script('return a=document.body.offsetHeight')
        cut_res = cut_img(height, self.dir_path, pic_name)
        if not cut_res.get('succ'):
            logger.error('got pic failed  ---  pic_name: %s' % pic_name)
        logger.info('got an pic: %s' % pic_name)
        self.d.refresh()
        return {'succ': True}

    def parse_balance(self, *args, **kwargs):
        header = ['账号', '余额']
        # data = [{'账号': self.acc, '余额': self.balance_data}]
        data = self.balance_data
        return header, data

    def get_balance(self):
        self.d.get('http://ad.izuiyou.com/')
        self.d.implicitly_wait(5)
        balance_data = self.d.find_element_by_css_selector('tr td:nth-child(2) strong').text.strip()
        self.balance_data = float(balance_data) if balance_data else 0

    def login_part(self, ui):
        self.login_obj = LoginZuiYou(ui)
        return self.login_obj.run_login()

    def deal_login_result(self, login_res):
        if not login_res.get('succ'):
            login_res['login'] = False
            return login_res
        self.d = login_res.get('driver')
        self.wait = WebDriverWait(self.d, 20)
        self._headers['Cookie'] = login_res.get('Cookie')

    def get_data_part(self, ui, **kwargs):
        mths, dates = u.make_dates(ys=None, ms=None, ye=None, me=None)
        data_res = []
        for sd, ed in dates:
            res = self.get_data(sd, ed)
            if res.get('msg') == 'no data':
                data_res.append((sd, ed, False))
                continue
            # save
            file_name = f'{sd}_{ed}.json'
            with open(join(self.dir_path, file_name), 'w', encoding='utf-8') as f:
                dump(res.get('msg'), f)
            data_res.append((sd, ed, True))

        data_list = [1 for a, b, c in data_res if c]
        if not data_list:
            self.result_kwargs['has_data'] = 0
        return data_res

    def get_img_part(self, get_data_res=None, **kwargs):
        for sd, ed, has_data in get_data_res:
            if not has_data:
                continue
            self.get_img(sd, ed)                # 报表部分
        return {'succ': True}
