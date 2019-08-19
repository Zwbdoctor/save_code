"""
cpa 2345 爬虫 ----  http://appunion.2345.com/   zwb 
"""

from json import dump
import os

from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.by import By
from lxml.html import etree

from platform_crawler.spiders.pylib.task_process import TaskProcess
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.utils.utils import Util


u = Util()
logger = None
base_header = {
    'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'Host': "appunion.2345.com",
    'Referer': "http://appunion.2345.com/index.php?c=exp&applist=8&start_date=&end_date=",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3569.0 Safari/537.36",
}


class Login2345:

    def __init__(self, ui):
        self.d = None
        self.wait = None
        self.user_info = ui
        self.acc, self.pwd = ui.get('account'), ui.get('password')

    def login(self):
        for e in range(3):
            try:
                self.d.get('http://appunion.2345.com/index.php')
                break
            except:
                continue
        self.wait.until(EC.visibility_of_element_located((By.ID, 'username'))).send_keys(self.acc)
        self.wait.until(EC.visibility_of_element_located((By.ID, 'userpass'))).send_keys(self.pwd)
        self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'btn_submit'))).click()
        self.d.implicitly_wait(3)
        try:
            self.wait.until(EC.visibility_of_element_located((By.ID, 'edit_btn')))
            cookie = self.d.get_cookie('PHPSESSID')
            headers = 'PHPSESSID=%s' % cookie.get('value')
            return {'succ': True, 'driver': self.d, 'Cookie': headers}
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


class Browser2345Spider(TaskProcess):

    def __init__(self, user_info, **kwargs):
        global logger
        super().__init__(headers=base_header, is_cpa=True, user_info=user_info, **kwargs)
        self.cookies = {}
        logger = self.logger

    def get_data_process(self, sd, ed):
        page = self.d.page_source
        html = etree.HTML(page)
        app_list = html.xpath('//*[@id="apps"]//li')
        for app in app_list:
            app_key = app.xpath('./@key')
            if not app_key:
                return {'succ': True, 'msg': 'no app'}
            app_name = app.xpath('string(./a)')
            file_name = '%s_%s_%s.json' % (app_name, sd, ed)
            res = self.get_data(sd, ed, app_key[0])
            if not res.get('succ'):
                logger.error('sth error about get data func: %s' % res)
                continue
            data = res.get('msg')
            if not data:
                return {'succ': True, 'msg': 'no data'}
            with open(os.path.join(self.dir_path, file_name), 'w', encoding='utf-8') as f:
                dump(data, f)
        return {'succ': True}

    def get_data(self, sd, ed, app):
        url = "http://appunion.2345.com/index.php?c=exp&applist=%s&start_date=%s&end_date=%s" % (app, sd, ed)
        res = self.deal_result(self.execute('GET', url, verify=False))
        if not res.get('succ') and not res.get('msg').get('message') == 'success':
            return res
        html = etree.HTML(res.get('msg'))
        trs = html.xpath('//*[@class="tcontent"]/tr')
        data = []
        for tr in trs:
            date = tr.xpath('string(./td[1])')
            if '查询汇总' in date:
                continue
            new_promotion = tr.xpath('string(./td[2])')
            data.append({'date': date, 'new_promotion': new_promotion})
        logger.debug(data)
        return {'succ': True, 'msg': data}

    def get_img(self, sd, ed, app):
        url = 'http://appunion.2345.com/index.php?c=exp&a=index&applist=%s&start_date=%s&end_date=%s' % (app, sd, ed)
        self.d.get(url)
        self.d.implicitly_wait(10)
        self.d.find_element_by_id('curapp').click()
        app_name = self.d.find_element_by_css_selector('#apps li[key="%s"] a' % app).text
        self.d.execute_script('document.querySelector("body").click()')
        pic_name = '%s_%s_%s.png' % (app_name, sd, ed)
        height = self.d.execute_script('return a=document.body.offsetHeight')
        cut_res = cut_img(height, self.dir_path, pic_name)
        if not cut_res.get('succ'):
            logger.error('got pic failed  ---  pic_name: %s' % pic_name)
        logger.info('got an pic: %s' % pic_name)
        return {'succ': True}

    def get_apps(self):
        app_list = self.d.find_elements_by_css_selector('#apps li')
        return [x.get_attribute('key') for x in app_list]

    def login_and_get_data(self, ui):
        lu = Login2345(ui).run_login()
        if not lu.get('succ'):
            return lu
        self.d = lu.get('driver')
        self.wait = WebDriverWait(self.d, 20)
        self._headers['Cookie'] = lu.get('Cookie')

        mths, dates = u.make_dates(ys=None, ms=None, ye=None, me=None)
        res_list = []
        for sd, ed in dates:
            res = self.get_data_process(sd, ed)
            if res.get('msg') in ['no data', 'no app']:
                res_list.append(0)
                continue
            res_list.append(1)

        if 1 not in res_list:       # 判断是否有数据
            return {'succ': True, 'msg': 'no data'}
        app_list = self.get_apps()
        self.d.get('http://appunion.2345.com/index.php?c=exp&a=index&applist=8&start_date=&end_date=')
        for sd, ed in dates:
            for app in app_list:
                self.get_img(sd, ed, app)
        self.d.quit()
        return {'succ': True}
