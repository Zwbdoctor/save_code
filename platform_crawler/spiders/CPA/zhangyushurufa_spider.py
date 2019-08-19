"""
cpa ZYSRF 章鱼输入法爬虫 ---- http://report.021.com/outdatacenter/login/in
"""
from json import dump
import os

from lxml.html import etree
from selenium import webdriver

from platform_crawler.spiders.pylib.task_process import TaskProcess
from platform_crawler.spiders.pylib.base_crawler import BaseCrawler
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.utils.utils import Util

# from platform_crawler.utils.scp_tool import init_dst_dir


logger = None
base_header = {
    'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'Content-Type': "application/x-www-form-urlencoded",
    'Host': "www.etjg.com",
    'Referer': "http://www.etjg.com/login.php",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3569.0 Safari/537.36",
}


class LoginZYZS(BaseCrawler):

    def __init__(self, ui):
        self.user_info = ui
        self.acc, self.pwd = ui.get('account'), ui.get('password')
        super().__init__(headers=base_header, spider=ui.get('platform'))

    def xpath(self, element, text):
        ele = element.xpath(text)
        return ele[0].strip() if isinstance(ele, list) and len(ele) > 0 else ''

    def deal_result(self, result, **kwargs):
        res = self.base_result(**kwargs)
        if not res.get('succ'):
            return res
        html = res.get('msg')
        html = etree.HTML(html)
        if self.xpath(html, '//title/text()') == '登录首页':
            return {'succ': False, 'msg': 'login failed'}
        res['headers'] = self._headers
        return res

    def login(self):
        url = "http://report.021.com/outdatacenter/login/in"
        payload = {'username': self.acc, 'password': self.pwd}
        headers = {
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            'Content-Type': "application/x-www-form-urlencoded",
            'Host': "report.021.com",
            'Origin': "http://report.021.com",
            'Referer': "http://report.021.com/outdatacenter/login/in",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3569.0 Safari/537.36",
        }
        return self.deal_result(self.execute('POST', url, data=payload, headers=headers, verify=False, set_cookies=True), get_cookie=True)

    def run_login(self):
        for i in range(5):
            try:
                res = self.login()
                if res.get('succ'):
                    logger.info('login success --- acc --- %s' % self.acc)
                    return res
            except Exception as er:
                logger.error(er, exc_info=1)
                continue
        else:
            # params = [self.user_info.get('id'), self.user_info.get('account'), self.user_info.get('platform'), None, False]
            # if not post_res(*params):
            #     logger.error('----------useless account! Post result failed!')
            # else:
            logger.info('useless account!(%s) Post success!' % self.user_info.get('account'))
            return {'succ': False, 'invalid_account': True}


class ZYZSSpider(TaskProcess):

    def __init__(self, user_info, **kwargs):
        global logger
        self.cookies = {}
        super().__init__(user_info=user_info, is_cpa=True, **kwargs)
        logger = self.logger

    def xpath(self, element, text):
        ele = element.xpath(text)
        return ele[0].strip() if isinstance(ele, list) and len(ele) > 0 else ''

    def get_data(self, day):
        day = day.replace('-', '')
        url = 'http://report.021.com/outdatacenter/zhangyudata/qidlist?startDate=%s' % day
        self._headers['referer'] = 'http://report.021.com/outdatacenter/zhangyudata/qidlist'
        res = self.deal_result(self.execute('GET', url))
        if not res.get('succ'):
            return res
        html = etree.HTML(res.get('msg'))
        data = []
        for tr in html.xpath('//table/tbody/tr'):
            i = {}
            i['channel'] = tr.xpath('string(./td[2])')
            i['install_num'] = self.xpath(tr, './td[3]/text()')
            i['start_keyboard_rates'] = self.xpath(tr, 'td[4]/text()')
            data.append(i)
            logger.debug('crawled date --- %s' % i)
        return {'succ': True, 'data': data}

    def get_data_process(self, day):
        res = self.get_data(day)
        if not res.get('succ'):
            return res
        data = {'datas': res.get('data'), 'date': day}
        file_name = '%s.json' % day
        msg = ''
        if not res.get('data'):
            msg = 'no data'
            data = {'msg': msg}
        with open(os.path.join(self.dir_path, file_name), 'w', encoding='utf-8') as f:
            dump(data, f)
        return {'succ': True, 'msg': msg}

    def init_chrome(self, ui):
        self.d = webdriver.Chrome()
        self.d.set_page_load_timeout(60)
        self.d.set_script_timeout(30)
        self.d.maximize_window()
        from selenium.webdriver.support.wait import WebDriverWait
        self.wait = WebDriverWait(self.d, 20)
        # get page
        url = 'http://report.021.com/outdatacenter/login/in'
        self.d.get(url)
        self.d.implicitly_wait(5)
        self.d.find_element_by_id('username').send_keys(ui.get('account'))
        self.d.find_element_by_id('password').send_keys(ui.get('password'))
        self.d.find_element_by_id('stbn').click()
        self.d.implicitly_wait(5)

    def get_img(self, sd):
        sd = sd.replace('-', '')
        self.d.switch_to.frame('iframepage')
        self.d.execute_script('$.datepicker._selectDate("#startDate", "%s")' % sd)
        self.d.implicitly_wait(5)
        pic_name = '%s.png' % sd
        # height = self.d.execute_script('return document.querySelector("html").offsetHeight')
        cut_res = cut_img(None, self.dir_path, pic_name)
        if not cut_res.get('succ'):
            logger.error(cut_res.get('msg'))
        logger.info('got an pic: %s' % pic_name)
        # self.d.execute_script('back()')
        self.d.switch_to.default_content()

    def login_and_get_data(self, ui):
        lu = LoginZYZS(ui).run_login()
        if not lu.get('succ'):
            return lu
        self.cookies = lu.get('cookie')
        self._headers = lu.get('headers')

        mths, days = Util().make_days(ys=None, ms=None, ye=None, me=None)
        empty_day = []
        for day in days:
            logger.info('crawler day ----- %s' % day)
            res = self.get_data_process(day)
            if not res.get('succ'):
                return res
            if res.get('msg') == 'no data':
                empty_day.append(day)

        try:
            self.init_chrome(ui)
            for sd in days:
                if sd in empty_day:
                    continue
                self.get_img(sd)
        except Exception as es:
            logger.error(es, exc_info=1)
        finally:
            self.d.quit()
        return {'succ': True}
