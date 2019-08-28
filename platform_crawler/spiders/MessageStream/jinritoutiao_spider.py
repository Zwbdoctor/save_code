"""
信息流 今日头条 爬虫 ----  https://ad.toutiao.com/pages/login/index.html   zwb
--- Version 2.0
"""
from json import dump
from time import sleep
import os

from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.by import By

from platform_crawler.spiders.pylib.task_process import TaskProcess
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.utils.utils import Util
from platform_crawler.settings import join, IMG_PATH, JS_PATH


u = Util()
logger = None
base_header = {
    'Accept': "application/json, text/javascript, */*; q=0.01",
    'Host': "ad.oceanengine.com",
    'Referer': "https://ad.oceanengine.com/overture/data/advertiser/ad/",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
}


class LoginTouTiao:

    def __init__(self, ui):
        self.d = None
        self.wait = None
        self.user_info = ui
        self.acc, self.pwd = ui.get('account'), ui.get('password')

    def deal_vc(self):
        vc_name = join(IMG_PATH, 'vc_img.png')
        self.d.save_screenshot(vc_name)
        element = self.d.find_element_by_css_selector('section div:nth-child(3) div:nth-child(6) div')
        u.cutimg_by_driver(self.d, element, vc_name, chx=-15, chy=0)
        with open(vc_name, 'br') as f:
            im = f.read()
        res = u.rc.rk_create(im, '3040')
        vk = res.get('Result')
        return res, vk, im

    def is_login(self):
        global base_header
        import requests
        from time import time
        from json.decoder import JSONDecodeError
        url = 'https://ad.oceanengine.com/overture/index/account_balance/?_=%s' % int(time()*100)
        cks = self.d.get_cookies()
        cookie = '; '.join(['%s=%s' % (x.get('name'), x.get('value')) for x in cks])
        base_header['Cookie'] = cookie
        try:
            resp = requests.get(url, headers=base_header, timeout=60, verify=False)
            if resp.status_code != 200:
                logger.error(resp.text)
                return {'succ': False}
            res = resp.json()
            if res.get('status') == 'success':
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
                self.d.get('https://ad.oceanengine.com/pages/login/index.html')
                break
            except:
                continue
        self.d.implicitly_wait(10)
        sleep(1)
        login_way = self.d.find_element_by_xpath('//section/div/div').text
        if '密码登录' in login_way:
            self.d.execute_script("document.querySelectorAll('section > div > div span')[1].click()")
        self.d.find_element_by_css_selector("div[data-login-type-value='email']").click()
        self.wait.until(EC.visibility_of_element_located((By.NAME, 'account'))).send_keys(self.acc)
        self.wait.until(EC.visibility_of_element_located((By.NAME, 'password'))).send_keys(self.pwd)
        vc_obj, vc, im = self.deal_vc()
        self.d.find_element_by_name('captcha').send_keys(vc)
        self.d.find_element_by_css_selector('section div:nth-child(3) div:nth-child(10) div').click()
        self.d.implicitly_wait(10)
        sleep(3)
        with open(join(JS_PATH, 'delete_mask.js')) as f:
            del_mask_js = f.read()
        self.d.execute_script(del_mask_js % '.mobile-drainage')
        try:
            res = self.is_login()
            if not res.get('succ'):
                u.rc.rk_report_error(vc_obj.get('Id'))      # 验证结果上报
                return res
            u.rc.rk_report(im, 3040, vc, vc_type=self.user_info.get('platform'))
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
            logger.info('useless account!(%s) Post success!' % self.user_info.get('account'))
            self.d.quit()
            return {'succ': False, 'invalid_account': True}


class JinRiTouTiaoSpider(TaskProcess):

    def __init__(self, user_info, **kwargs):
        global logger
        super().__init__(headers=base_header, user_info=user_info, **kwargs)
        logger = self.logger

    def get_flow_data(self, sd, ed, page=1, accumulate=None):
        # 财务流水
        url = f'https://ad.oceanengine.com/overture/cash/get_cash_flow/?page={page}&start_date={sd}&end_date={ed}'
        ref = 'https://ad.oceanengine.com/overture/cash/flow/'
        res = self.deal_result(self.execute('GET', url, referer=ref, verify=False), json_str=True)
        if not res.get('succ') or res.get('msg').get('status') != 'success':
            return res
        data = res.get('msg').get('data')
        accu = [] if not accumulate else accumulate
        get_key = ['date', 'cash_cost', 'reward_cost']
        f = lambda a, b: round(a.get(b)/100000, 2) if b != 'date' else a.get(b)
        z = lambda x: {k: f(x, k) for k in get_key}
        accu.extend([z(x) for x in data.get('items')])
        if data.get('pagination').get('total_count') > 20 and data.get('pagination').get('page') == 1:
            return self.get_flow_data(sd, ed, page=2, accumulate=accu)
        return {'succ': True, 'msg': accu}

    def get_data(self, sd, ed):
        url = "https://ad.oceanengine.com/statistics/report/advertiser_stat/?st=%s&et=%s&day=1&compare=0" % (sd, ed)
        # 消耗数据
        ref = 'https://ad.oceanengine.com/overture/reporter/advertiser/'
        res = self.deal_result(self.execute('GET', url, verify=False, referer=ref), json_str=True)
        if not res.get('succ') or res.get('msg').get('status') != 'success':
            return res
        data = res.get('msg')
        has_data = {'ad_data': 1, 'flow_data': 1}
        if not data.get('data').get('advertiser_data'):
            has_data['ad_data'] = 0
        # 财务流水
        flow_data = self.get_flow_data(sd, ed)
        if not flow_data.get('succ'):
            return flow_data
        if not flow_data.get('msg'):
            has_data['flow_data'] = 0
        # 合并
        for item in data.get('data').get('advertiser_data'):
            for i in flow_data.get('msg'):
                if i.get('date') == item.get('create_time'):
                    i.pop('date')
                    item.update(i)
                    break
        logger.info('month: %s~%s --- %s' % (sd, ed, data))
        if 1 not in has_data.values():
            return {'succ': True, 'msg': 'no data'}
        return {'succ': True, 'msg': data, 'has_data': has_data}

    def get_img(self, sd, ed, flow=False):
        # 报表部分
        url = f'https://ad.oceanengine.com/overture/reporter/advertiser/?st={sd}&et={ed}'
        js = None
        if flow:
            # 财务流水部分
            url = 'https://ad.oceanengine.com/overture/cash/flow/'
            with open(join(JS_PATH, 'ad_toutiao.js'), 'r', encoding='utf-8') as j:
                js = j.read()
        self.d.get(url)
        self.d.implicitly_wait(10)
        delete_mask = """
        ele = document.querySelector('.user-guide');
        if (ele){ele.remove();}"""
        self.d.execute_script(delete_mask)
        if flow:
            self.d.execute_script(js % (sd, ed))
        pic_name = f'{sd}_{ed}.png' if not flow else f'财务流水_{sd}_{ed}.png'
        height = self.d.execute_script('return a=document.body.offsetHeight')
        cut_res = cut_img(height, self.dir_path, pic_name)
        if not cut_res.get('succ'):
            logger.error('got pic failed  ---  pic_name: %s' % pic_name)
        logger.info('got an pic: %s' % pic_name)
        return {'succ': True}

    def parse_balance(self):
        url = 'https://ad.oceanengine.com/overture/index/account_balance/'
        ref = 'https://ad.oceanengine.com/overture/data/advertiser/ad/'
        res = self.deal_result(self.execute('GET', url, referer=ref, verify=False), json_str=True)
        if not res.get('succ'):
            raise Exception(res.get('msg'))
        data = res.get('msg').get('data')
        balance = {'账号': self.acc, '余额': data.get('valid_cash')}
        header = ['账号', '余额']
        logger.info(balance)
        return header, data.get('valid_cash')

    def login_part(self, ui):
        return LoginTouTiao(ui).run_login()

    def agree_proto(self):
        try:
            self.d.switch_to.frame(self.d.find_element_by_id('ad-agreement'))
            self.wait_element(By.CSS_SELECTOR, 'div.bui-icon-check', wait_time=2, ec=EC.presence_of_element_located).click()
            self.wait_element(By.CSS_SELECTOR, '.ad-agreement-container .bui-btn-md').click()
        except:
            pass
        self.d.switch_to_default_content()

    def deal_login_result(self, login_res):
        if not login_res.get('succ'):
            login_res['login'] = False
            return login_res
        self.d = login_res.get('driver')
        self.wait = WebDriverWait(self.d, 20)
        self._headers = base_header
        self.agree_proto()

    def get_data_part(self, ui):
        # get data
        mths, dates = u.make_dates(ys=None, ms=None, ye=None, me=None)
        data_res = []
        for sd, ed in dates:
            res = self.get_data(sd, ed)
            if res.get('msg') == 'no data':
                data_res.append((sd, ed, False, 0))
                continue
            # save
            file_name = f'{sd}_{ed}.json'
            with open(os.path.join(self.dir_path, file_name), 'w', encoding='utf-8') as f:
                dump(res.get('msg'), f)
            data_res.append((sd, ed, True, res.get('has_data')))

        datas = [1 for x in data_res if x[2]]
        if not datas:
            self.result_kwargs['has_data'] = 0
        return data_res

    def get_img_part(self, get_data_res=None, **kwargs):
        # get img
        for sd, ed, has_data, d_type in get_data_res:
            if not has_data:
                continue
            if d_type.get('ad_data') == 1:
                self.get_img(sd, ed)                # 报表部分
            if d_type.get('flow_data') == 1:
                self.get_img(sd, ed, flow=True)     # 财务流水部分
        self.d.quit()
        return {'succ': True}
