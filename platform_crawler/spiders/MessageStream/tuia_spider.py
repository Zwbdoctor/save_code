"""
信息流 推啊平台 爬虫 ----  zwb
"""
from json import dump
from time import sleep

from selenium.webdriver.support.wait import WebDriverWait
from requests import get
from json.decoder import JSONDecodeError

from platform_crawler.spiders.pylib.task_process import TaskProcess
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.utils.utils import Util
from platform_crawler.settings import join, JS_PATH, DEFAULT_VERIFY_PATH

u = Util()
logger = None
base_header = {
    'Accept': "*/*",
    'Cookie': None,
    'Host': "www.tuia.cn",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36"
}


class LoginTuiA:

    def __init__(self, ui):
        self.d = None
        self.wait = None
        self.user_info = ui
        self.acc, self.pwd = ui.get('account'), ui.get('password')

    def deal_vc(self):
        vc_name = DEFAULT_VERIFY_PATH
        self.d.save_screenshot(vc_name)
        element = self.d.find_element_by_id('captcha')
        u.cutimg_by_driver(self.d, element, vc_name)
        with open(vc_name, 'br') as f:
            im = f.read()
        res = u.rc.rk_create(im, 3040)
        vk = res.get('Result')
        return res, vk, im

    def is_login(self):
        url = 'http://www.tuia.cn/account/getAccountInfo'
        cks = self.d.get_cookies()
        cookie = '; '.join(['%s=%s' % (x.get('name'), x.get('value')) for x in cks])
        headers = {
            'Accept': "*/*",
            'Cookie': cookie,
            'Host': "www.tuia.cn",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
        }
        try:
            resp = get(url, headers=headers, timeout=60)
            if resp.status_code != 200:
                logger.error(resp.text)
                return {'succ': False}
            res = resp.json()
            if res.get('code') == "0":
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
                self.d.get('http://www.tuia.cn/public.html#/signin')
                break
            except:
                continue
        self.d.implicitly_wait(10)
        sleep(1)
        self.d.find_element_by_css_selector('input[type="text"]').send_keys(self.acc)
        self.d.find_element_by_css_selector('input[type="password"]').send_keys(self.pwd)
        self.d.find_element_by_class_name('ta-btn-blue').click()
        sleep(3)
        try:
            res = self.is_login()
            if not res.get('succ'):
                return res
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
            logger.info('useless account!(%s) Post success!' % self.user_info.get('account'))
            self.d.quit()
            return {'succ': False, 'invalid_account': True}


class TuiASpider(TaskProcess):

    def __init__(self, user_info, **kwargs):
        global logger
        super().__init__(headers=base_header, user_info=user_info, **kwargs)
        logger = self.logger

    def get_data(self, sd, ed, page=1, data=None):
        url = "http://www.tuia.cn/advert/queryAdvertData"
        payload = {"startDate": sd, "endDate": ed, "type": "1", "pageSize": "50",
                   "currentPage": str(page)}
        res = self.deal_result(self.execute('GET', url, params=payload), json_str=True)
        if not res.get('succ') or res.get('msg').get('code') != '0':
            return res
        total_page = res.get('msg').get('data').get('totalPage')
        data = data if isinstance(data, list) else []
        data.extend(res.get('msg').get('data').get('list'))
        if not data:
            return {'succ': True, 'msg': 'no data'}
        if page != total_page:
            page += 1
            return self.get_data(sd, ed, page, data=data)
        logger.info('month: %s~%s --- %s' % (sd, ed, data))
        return {'succ': True, 'msg': data}

    def change_date(self, sd, ed):
        with open(join(JS_PATH, 'tuia.js'), 'r', encoding='utf-8') as f:
            js = f.read()
        self.d.execute_script(js % (sd, ed))
        sleep(1)

    def get_img(self, sd, ed, total=False):
        # 报表部分
        url = 'http://www.tuia.cn/private.html#/addata'
        self.d.get(url)
        self.d.implicitly_wait(10)
        sleep(1.5)
        selected = self.d.execute_script('return a=document.querySelector("#type").checked')
        if total and selected:  # 总数据
            self.d.find_element_by_id('type').click()
        elif not total and not selected:
            self.d.find_element_by_id('type').click()
        self.change_date(sd, ed)
        page = 1
        while True:
            pic_name = f'{sd}_{ed}_p{page}.png' if not total else f'total_{sd}_{ed}_p{page}.png'
            height = self.d.execute_script('''return a1 = document.querySelector("#app").offsetHeight;''')
            # print(f'page:{page} | height:{height} | total:{total} | selected:{selected}')
            cut_res = cut_img(height, self.dir_path, pic_name)
            if not cut_res.get('succ'):
                logger.error('got pic failed  ---  pic_name: %s' % pic_name)
            logger.info('got an pic: %s' % pic_name)
            next_page = self.d.find_element_by_css_selector('li[title="下一页"]')
            next_page_disable = next_page.get_attribute('aria-disabled')
            if next_page_disable == 'true':
                break
            next_page.click()
            sleep(1)
            page += 1
            self.d.execute_script('document.documentElement.scrollTop = 0')
        return {'succ': True}

    def parse_balance(self):
        url = 'http://www.tuia.cn/finance/getFinance'
        ref = 'http://www.tuia.cn/private.html'
        res = self.deal_result(self.execute('GET', url, referer=ref), json_str=True)
        if not res.get('succ'):
            raise Exception(res.get('msg'))
        balance = res.get('msg').get('data').get('balance')/100
        header = ['账号', '余额']
        # data = [{'账号': self.acc, '余额': balance}]
        return header, balance

    def login_part(self, ui):
        self.login_obj = LoginTuiA(ui)
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
        if len(data_list) == 0:
            self.result_kwargs['has_data'] = 0
        return data_res

    def get_img_part(self, get_data_res=None, **kwargs):
        for sd, ed, has_data in get_data_res:
            if not has_data:
                continue
            self.get_img(sd, ed, total=True)
            self.get_img(sd, ed)
        return {'succ': True}
