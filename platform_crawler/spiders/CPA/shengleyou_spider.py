"""
cpa 圣乐游 财务爬虫 ---- http://www.etjg.com/
"""
# from re import search
# import logging
from json import dump
import os
import time
import re

from lxml.html import etree

from platform_crawler.spiders.pylib.task_process import TaskProcess
from platform_crawler.spiders.pylib.base_crawler import BaseCrawler
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.utils.utils import Util
# from platform_crawler.settings import IMG_PATH, join


# from platform_crawler.utils.scp_tool import init_dst_dir


logger = None
base_header = {
    'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'Content-Type': "application/x-www-form-urlencoded",
    'Host': "www.etjg.com",
    'Referer': "http://www.etjg.com/login.php",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3569.0 Safari/537.36",
}


class LoginSYL(BaseCrawler):

    def __init__(self, ui):
        self.user_info = ui
        self.acc, self.pwd = ui.get('account'), ui.get('password')
        self.datapass = ui.get('data_pass')
        super().__init__(spider='%s.task_process' % ui.get('platform'), headers=base_header)

    def is_login(self, res):
        time.sleep(3)
        import re
        try:
            msg = re.search(r'document.write\("([\u4e00-\u9fa5]+)"\)', res.get('msg')).group(1)
            if msg != '登录成功':
                logger.info('login failed, detail msg:%s' % msg)
                return {'succ': False, 'msg': msg}
            else:
                logger.info('login success  --- account: %s' % self.acc)
                return {'succ': True}
        except Exception as e:
            logger.error(e, exc_info=1)
            return {'succ': False}

    def set_sessionid(self):
        url = 'http://www.etjg.com/member/'
        return self.deal_result(self.execute('GET', url, verify=False, set_cookies=True), get_cookie=True)

    def run(self):
        url = 'http://www.etjg.com/login.php?action=login'
        payload = {'email': self.acc, 'pass': self.pwd, 'button': '%E7%AB%8B%E5%8D%B3%E7%99%BB%E5%BD%95'}
        res = self.deal_result(self.execute('POST', url, data=payload, verify=False, set_cookies=True), get_cookie=True, encoding='utf-8')
        if not res.get('succ'):
            return res
        msg = self.is_login(res)
        if not msg.get('succ'):
            return msg
        res = self.set_sessionid()
        return {'succ': True, 'cookie': res.get('cookie'), 'headers': self._headers}

    def run_login(self):
        res = {}
        for i in range(5):
            try:
                res = self.run()
                if res.get('succ'):
                    break
            except Exception as e:
                logger.error(e, exc_info=1)
                res = {'succ': False}
        if not res.get('succ'):
            # params = [self.user_info.get('id'), self.user_info.get('account'), self.user_info.get('platform'), None,
            #           False]
            # if not post_res(*params):
            #     logger.error('login failed, post failed')
            logger.info('login failed, post success')
            res['invalid_account'] = True
        return res


class SLYSpider(TaskProcess):

    def __init__(self, user_info, **kwargs):
        global logger
        self.cookies = {}
        self.cookie_jar = []
        super().__init__(is_cpa=True, user_info=user_info, **kwargs)
        logger = self.logger

    def xpath(self, element, text):
        ele = element.xpath(text)
        return ele[0].strip() if isinstance(ele, list) and len(ele) > 0 else ''

    def init_driver(self):
        from selenium import webdriver
        self.d = webdriver.Chrome()
        self.d.delete_all_cookies()
        self.d.maximize_window()

    def driver_get(self, url):
        for e in range(3):
            try:
                self.d.get(url)
                logger.debug('driver_get url --- %s' % url)
                break
            except:
                continue

    def get_data_process(self, sd, ed):
        file_name = '%s_%s.json' % (sd, ed)
        res = self.get_data(sd, ed)
        if not res.get('succ'):
            return res
        data = res.get('msg')
        if not data:
            return {'succ': True, 'msg': 'no data'}
        with open(os.path.join(self.dir_path, file_name), 'w', encoding='utf-8') as f:
            dump(data, f)
        return res

    def parse(self, page):
        html = etree.HTML(page)
        trs = html.xpath('//table[@class="table_main"]//tr')[1:-1]
        data = []
        for tr in trs:
            i = {}
            i['date'] = self.xpath(tr, './td[1]/text()')
            i['pname'] = self.xpath(tr, './td[2]/text()')
            i['mid'] = self.xpath(tr, './td[3]/text()')
            i['click_num'] = self.xpath(tr, './td[4]/text()')
            i['business_num'] = self.xpath(tr, './td[5]/text()')
            i['per_price'] = self.xpath(tr, './td[6]/text()')
            i['price'] = self.xpath(tr, './td[7]/font/text()')
            i['data_status'] = self.xpath(tr, './td[8]/font/text()')
            i['settle_status'] = self.xpath(tr, './td[9]/font/text()')
            i['belong_to'] = self.xpath(tr, './td[10]/text()')
            data.append(i)
            logger.debug('crawled data: --- %s' % i)
        return data

    def get_data(self, sd, ed):
        url = "http://www.etjg.com/member/data.php"
        params = {"cate": "1", "province": "0", "city": "0", "daili": "", "date": sd, "status": "", "p": "",
                  "enddate": ed, "channelid": "", "page": '1'}
        res = self.deal_result(self.execute('GET', url, params=params, verify=False), encoding='utf-8')
        if not res.get('succ'):
            return res
        data = self.parse(res.get('msg'))
        html = etree.HTML(res.get('msg'))
        pgs = html.xpath('//div[@class="pagemain"]//a[@class="page_pre"]')[-1:]
        if not pgs:
            return {'succ': True, 'msg': data}
        pgs = pgs[0].xpath('./@href')[0]
        pgs = re.search(r'page=(\d+)', pgs).group(1)
        for idx in range(2, int(pgs)+1):
            params['page'] = str(idx)
            res = self.deal_result(self.execute('GET', url, params=params, verify=False), encoding='utf-8')
            if not res.get('succ'):
                return res
            data.extend(self.parse(res.get('msg')))
            logger.info('--- Page ---  --- %s/%s ---' % (idx, int(pgs)))

        return {'succ': True, 'msg': data, 'pages': pgs}

    def change_date(self, sd, ed):
        self.d.switch_to.frame('right')
        self.d.execute_script("document.querySelector('#date').value='%s';" % sd)
        self.d.execute_script("document.querySelector('#enddate').value='%s';" % ed)
        self.d.execute_script("document.querySelector('#button').click();")

    def get_img_process(self, sd, ed):
        self.change_date(sd, ed)
        total_page = self.d.find_elements_by_class_name('page_pre')[-1].get_attribute('href')
        index = total_page[total_page.rfind('page'):]
        total_page = int(index[index.rfind('=')+1:])
        for p in range(total_page):
            img_name = '%s_%s_p%s.png' % (sd, ed, p+1)
            cut_res = cut_img(None, self.dir_path, img_name)
            if not cut_res['succ']:
                logger.error('get img %s failed-------msg: %s' % (img_name, cut_res.get('msg')))
            logger.info('got img: --- picname: %s' % img_name)
            try:
                self.d.find_elements_by_class_name('page_pre')[-2].click()
            except:
                continue
        else:
            self.d.switch_to.default_content()
        return {'succ': True}

    def login_and_get_data(self, ui):
        lu = LoginSYL(ui).run_login()
        if not lu.get('succ'):
            return lu
        self.cookies = lu.get('cookie')
        self.cookie_jar = [{'name': e.split('=')[0], 'value': e.split('=')[1]} for e in self.cookies.split('; ')]
        self._headers = lu.get('headers')

        ys, ms, ye, me = ui.get('date') if ui.get('date') else (None, None, None, None)
        mths, dates = Util().make_dates(ys=ys, ms=ms, ye=ye, me=me)
        pages_list = []
        data_list = []
        for sd, ed in dates:
            res = self.get_data_process(sd, ed)
            if not res.get('succ'):
                return res
            if res.get('msg') == 'no data':
                continue
            data_list.append(1)
            pages_list.append((sd, ed, res.get('pages')))
            logger.info('crawled month range ----- %s ~ %s' % (sd, ed))
        if len(data_list) == 0:
            return {'succ': True, 'msg': 'no data'}

        url = 'http://www.etjg.com/member/'
        self.init_driver()
        self.driver_get(url)
        for c in self.cookie_jar:
            self.d.add_cookie(c)
        self.driver_get(url)
        for sd, ed, p in pages_list:
            if not p:
                continue
            self.get_img_process(sd, ed)
        self.d.quit()
        return {'succ': True}
