"""
信息流 猎户平台 爬虫 ----  zwb
"""
from json import dump
from time import sleep
import os
import json

from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.by import By
from requests.utils import quote

from platform_crawler.spiders.pylib.task_process import TaskProcess
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.utils.utils import Util
from platform_crawler.settings import join, IMG_PATH, JS_PATH

u = Util()
logger = None
base_header = {
    'Accept': "application/json, text/plain, */*",
    'Cookie': None,
    'Host': "can.cmcm.com",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36"
}


class LoginLieHu:

    def __init__(self, ui):
        self.d = None
        self.wait = None
        self.user_info = ui
        self.acc, self.pwd = ui.get('account'), ui.get('password')

    def deal_vc(self):
        vc_name = join(IMG_PATH, 'vc_img.png')
        self.d.save_screenshot(vc_name)
        element = self.d.find_element_by_id('captcha')
        u.cutimg_by_driver(self.d, element, vc_name)
        with open(vc_name, 'br') as f:
            im = f.read()
        res = u.rc.rk_create(im, 3040)
        vk = res.get('Result')
        return res, vk, im

    def is_login(self):
        from requests import get
        from json.decoder import JSONDecodeError
        url = 'http://can.cmcm.com/api/message/show?status=0&dosubmit=1&count=10000'
        cks = self.d.get_cookies()
        cookie = '; '.join(['%s=%s' % (x.get('name'), x.get('value')) for x in cks])
        headers = {
            'Accept': "application/json, text/plain, */*",
            'Cookie': cookie,
            'Host': "can.cmcm.com",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
        }
        try:
            resp = get(url, headers=headers, timeout=60)
            if resp.status_code != 200:
                logger.error(resp.text)
                return {'succ': False}
            res = resp.json()
            if res.get('status') == 200:
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
                self.d.get('http://can.cmcm.com/login/index.html')
                break
            except:
                continue
        self.d.implicitly_wait(10)
        sleep(1)
        self.d.find_element_by_id('email').send_keys(self.acc)
        self.d.find_element_by_id('password').send_keys(self.pwd)
        vc_obj, vc, im = self.deal_vc()
        self.d.find_element_by_id('verify-code').send_keys(vc)
        self.d.find_element_by_class_name('mybtn').click()
        sleep(3)
        try:
            res = self.is_login()
            if not res.get('succ'):
                u.rc.rk_report_error(vc_obj.get('Id'))  # 验证结果上报
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
            logger.error('----------useless account! Post result failed!')
            self.d.quit()
            return {'succ': False, 'invalid_account': True}


class LieHuSpider(TaskProcess):

    def __init__(self, user_info, **kwargs):
        global logger
        super().__init__(headers=base_header, user_info=user_info, **kwargs)
        logger = self.logger

    def parse_data(self, content):
        title = content.get('title_en')
        data = content.get('data')
        z = [{k: v.replace('￥', '').replace(',', '') for k, v in zip(title, i)} for i in data]
        content['data'] = z
        cost = content.get('sum')[6].replace('￥', '').replace(',', '')
        if float(cost) == 0:
            return None
        return content

    def get_data(self, sd, ed, acc):
        url = "http://can.cmcm.com/api/report/planreport"
        payload = {"column": ["thedate", "pv", "click", "ctr", "orion_install", "orion_cvr", "cost", "cpm"],
                   "dimension": ["thedate"], "filter": {}, "advanced": {"pv": {"op": "top", "value": "10000"}},
                   "start": sd, "end": ed, "report": "report",
                   "emailAddress": acc, "ps": 100}
        self._headers['Content-Type'] = 'application/x-www-form-urlencoded'
        res = self.deal_result(self.execute('POST', url, data=f'q={quote(json.dumps(payload))}'), json_str=True)
        if not res.get('succ') or res.get('msg').get('status') != 200:
            return res
        data = res.get('msg').get('content')
        data = self.parse_data(data)
        if not data:
            return {'succ': False, 'msg': 'no data'}
        logger.info('month: %s~%s --- %s' % (sd, ed, data))
        return {'succ': True, 'msg': data}

    def change_date(self, sd, ed):
        with open(join(JS_PATH, 'liehu.js'), 'r', encoding='utf-8') as f:
            js = f.read()
        lsd = sd.replace('-', '/')[5:]
        led = sd.replace('-', '/')[5:]
        self.d.execute_script(js % (lsd, led, sd, ed))

    def get_img(self, sd, ed):
        # 报表部分
        url = 'http://can.cmcm.com/report/index.html'
        self.d.get(url)
        self.d.implicitly_wait(10)
        self.change_date(sd, ed)
        pic_name = f'{sd}_{ed}.png'
        self.wait_element(By.CSS_SELECTOR, '.tablesorter-headerRow', ec=EC.presence_of_element_located)
        height = self.d.execute_script('return a=document.querySelector("#reportTableWrapper table").offsetHeight + document.body.offsetHeight')
        cut_res = cut_img(height, self.dir_path, pic_name)
        if not cut_res.get('succ'):
            logger.error('got pic failed  ---  pic_name: %s' % pic_name)
        logger.info('got an pic: %s' % pic_name)
        self.d.refresh()
        return {'succ': True}

    def parse_balance(self):
        data = float(self.balance_data) if self.balance_data else 0
        data = [{'账号': self.acc, '余额': data}]
        header = ['账号', '余额']
        return header, data

    def login_part(self, ui):
        self.login_obj = LoginLieHu(ui)
        return self.login_obj.run_login()

    def deal_login_result(self, login_res):
        if not login_res.get('succ'):
            login_res['login'] = False
            return login_res
        self.d = login_res.get('driver')
        self.wait = WebDriverWait(self.d, 20)
        self._headers['Cookie'] = login_res.get('Cookie')
        self.balance_data = self.wait_element(By.CSS_SELECTOR, '.font-number.balance-num',
                                              EC.presence_of_element_located).text.strip()

    def get_data_part(self, ui, **kwargs):
        dates = self.get_dates
        data_res = []
        for sd, ed in dates:
            res = self.get_data(sd, ed, ui.get('account'))
            if res.get('msg') == 'no data':
                data_res.append((sd, ed, False))
                logger.info(f'date_range: {sd}~{ed} | no data')
                continue
            # save
            file_name = f'{sd}_{ed}.json'
            with open(os.path.join(self.dir_path, file_name), 'w', encoding='utf-8') as f:
                dump(res.get('msg'), f)
            data_res.append((sd, ed, True))

        datas = [1 for a, b, c in data_res if c]
        if not datas:
            self.result_kwargs['has_data'] = 0
        return data_res

    def get_img_part(self, get_data_res=None, **kwargs):
        for sd, ed, has_data in get_data_res:
            if not has_data:
                continue
            self.get_img(sd, ed)  # 报表部分
        self.d.quit()
        return {'succ': True}
