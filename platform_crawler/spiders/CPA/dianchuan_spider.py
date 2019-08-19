"""
cpa 点传 爬虫 ----  http://3tkj.cn/xsoa2018/ad/platform/   zwb
"""

from json import dump
import os

from selenium.webdriver.support.wait import WebDriverWait
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


class LoginDC:

    def __init__(self, ui):
        self.d = None
        self.wait = None
        self.user_info = ui
        self.acc, self.pwd = ui.get('account'), ui.get('password')

    def login(self, acct_times=1):
        self.d.get('http://3tkj.cn/xsoa2018/ad/platform')
        self.d.implicitly_wait(5)
        self.d.find_element_by_id('user').send_keys(self.acc)
        self.d.find_element_by_id('word').send_keys(self.pwd)
        vc = self.d.find_element_by_id('checkCode').text
        self.d.find_element_by_id('inputcode').send_keys(vc)
        self.d.find_element_by_id('btn20').click()
        self.d.implicitly_wait(3)
        try:
            error_msg = self.d.find_element_by_class_name('error-tip').text.strip()
            if error_msg:
                if acct_times > 3:
                    return {'succ': False, 'msg': 'pwd'}
                acct_times += 1
                return self.login(acct_times=acct_times)
        except:
            cookies = self.d.get_cookies()
            return {'succ': True, 'driver': self.d, 'Cookie': cookies}

    def run_login(self, driver):
        self.d = driver
        for i in range(2):
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


class DCSpider(TaskProcess):

    def __init__(self, user_info, **kwargs):
        global logger
        super().__init__(is_cpa=True, user_info=user_info, headers=base_header, **kwargs)
        logger = self.logger
        self.cookies = {}

    def get_data_process(self, sd, ed, root_url):
        url = "%s&start_date=%s&end_date=%s&soft_id=" % (root_url, sd, ed)
        self.d.get(url)
        page = self.d.page_source
        html = etree.HTML(page)
        file_name = '%s_%s.json' % (sd, ed)
        res = self.get_data(html)
        if not res.get('succ'):
            logger.error('sth error about get data func: %s' % res)
            return {'succ': False}
        data = res.get('msg')
        if not data:
            return {'succ': True, 'msg': 'no data'}
        with open(os.path.join(self.dir_path, file_name), 'w', encoding='utf-8') as f:
            dump(data, f)
        return {'succ': True}

    def get_data(self, html):
        trs = html.xpath('//tr')[1:]
        data = []
        for tr in trs:
            date = tr.xpath('string(./td[1])')
            if '合计' in date:
                total = tr.xpath('string(./td[4])')
                data.append({'total': total})
                continue
            product_id = tr.xpath('string(./td[2])').strip()
            product_flag = tr.xpath('string(./td[3])').strip()
            num = tr.xpath('string(./td[4])').strip()
            data.append({'date': date, 'product_id': product_id, 'product_flag': product_flag, 'pnum': num})
        logger.debug(data)
        return {'succ': True, 'msg': data}

    def get_img(self, sd, ed, app_name, app_value, root_url):
        url = '%s&start_date=%s&end_date=%s&soft_id=%s' % (root_url, sd, ed, app_value)
        self.d.get(url)
        self.d.implicitly_wait(3)
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
        self.init_browser()
        lu = LoginDC(ui).run_login(self.d)
        if not lu.get('succ'):
            return lu
        self.d = lu.get('driver')
        self.wait = WebDriverWait(self.d, 20)
        self._headers['Cookie'] = lu.get('Cookie')

        # get app_list
        page = self.d.page_source
        html = etree.HTML(page)
        app_list = html.xpath('//select/option')[1:]
        for index, app in enumerate(app_list):
            app_value = app.xpath('./@value')[0]
            app_name = app.xpath('string(.)')
            app_list[index] = [app_name, app_value]

        # get data
        mths, dates = u.make_dates(ys=None, ms=None, ye=None, me=None)
        current_url = self.d.find_element_by_css_selector('.active').get_attribute('href')
        res_list = []
        for sd, ed in dates:
            res = self.get_data_process(sd, ed, current_url)
            if res.get('msg') == 'no data' and res.get('succ'):
                continue
            res_list.append(1)
        if len(res_list) == 0:
            return {'succ': True, 'msg': 'no data'}

        # get image with app
        for sd, ed in dates:
            for app_name, app_value in app_list:
                self.get_img(sd, ed, app_name, app_value, current_url)

        self.d.quit()
        return {'succ': True}
