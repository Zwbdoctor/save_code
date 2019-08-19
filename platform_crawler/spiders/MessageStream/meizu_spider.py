from selenium.webdriver.support.wait import WebDriverWait
import os
import json

from platform_crawler.utils.utils import Util
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.spiders.get_login_data.login_meizu import MeiZu
from platform_crawler.spiders.pylib.task_process import TaskProcess, settings

u = Util()
logger = None


class MeizuSpider(TaskProcess):

    def __init__(self, user_info, **kwargs):
        global logger
        self.u = u
        self.result_kwargs = {'has_data': 1, 'has_pic': 1}
        self.headers = {
            'Accept': "application/json, text/plain, */*",
            'Cookie': None,
            'Host': "mzdsp.meizu.com",
            'Referer': "http://mzdsp.meizu.com/views/home.html",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
        }
        self.cookie_str = None
        super().__init__(user_info=user_info, **kwargs)
        logger = self.logger

    def get_data(self, sd, ed):
        """
        获取数据
        """
        url = f"http://mzdsp.meizu.com/console/mdsp/stat/plan/list?startTime={sd}&endTime={ed}"
        # 处理文件名
        fname = f'{sd}_{ed}.json'
        file_name = os.path.join(self.dir_path, fname)
        # 处理数据
        self.headers.update({'Cookie': self.cookie_str})
        data = self.deal_result(self.execute('GET', url, headers=self.headers), json_str=True)
        if not data.get('succ'):
            raise Exception(data.get('msg'))
        data = data.get('msg')
        # 没有数据
        if data.get('value').get('total') == 0:
            logger.info(f'no data | range: {sd}~{ed}')
            return {'succ': False, 'msg': 'no data'}
        # 写入文件
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        logger.info('crawled data: --------%s' % data)
        return {'succ': True}

    def get_data_part(self, ui, **kwargs):
        # 获取时间
        dates = self.get_dates
        data_list = []
        for sd, ed in dates:
            # 获取数据
            logger.info('data_rage-----%s~%s' % (sd, ed))
            data_res = self.get_data(sd, ed)
            if not data_res.get('succ') and data_res.get('msg') == 'no data':
                continue
            data_list.append((sd, ed))
        if not data_list:
            self.result_kwargs['has_data'] = 0
        return data_list

    def set_date_with_js(self, sd, ed):
        # todo: rebuild set date js
        with open(settings.join(settings.JS_PATH, '', 'r'), encoding='utf-8') as j:
            js = j.read()
        self.execute(js % sd, ed)

    def get_img_part(self, get_data_res=None, **kwargs):
        for sd, ed in get_data_res:
            self.get_img(sd, ed)

    def get_img(self, sd, ed):
        """截图操作"""
        self.d.get('http://mzdsp.meizu.com/views/home.html#/analysis/PlanData')
        self.d.implicitly_wait(5)
        self.set_date_with_js(sd, ed)
        # 截图
        hjs = 'return h = document.body.offsetHeight'
        height = self.d.execute_script(hjs)
        pic_name = f'{sd}_{ed}.png'
        cut_res = cut_img(height, self.dir_path, pic_name)
        if not cut_res['succ']:
            logger.error(f'get img {pic_name} failed')
            raise Exception(cut_res.get('msg'))
        logger.info('height: %s ---picname: %s' % (height, pic_name))

    def parse_balance(self):
        self.d.get('http://mzdsp.meizu.com/views/home.html')
        cookies = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in self.d.get_cookies()])
        url = 'http://mzdsp.meizu.com/console/mdsp/stat/sponsor/accountState'
        ref = 'http://mzdsp.meizu.com/views/home.html'
        self.headers.update({'Cookie': cookies, 'Referer': ref})
        res = self.deal_result(self.execute('GET', url, referer=ref, headers=self.headers), json_str=True)
        if not res.get('succ'):
            raise Exception(res.get('msg'))
        balance = res.get('msg').get('value').get('accountBalance')
        header = ['账号', '余额']
        data = [{'账号': self.acc, '余额': balance}]
        return header, data

    def login_part(self, ui):
        self.login_obj = MeiZu(ui, '%s.login' % ui.get('platform'))
        return self.login_obj.run_login()

    def deal_login_result(self, login_res):
        if not login_res.get('succ'):
            return login_res
        self.d = login_res.get('driver')
        self.wait = WebDriverWait(self.d, 20)
        cookies = login_res.get('cookies')
        self.cookie_str = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in cookies])
