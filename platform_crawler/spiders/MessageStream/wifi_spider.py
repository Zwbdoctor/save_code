import time
import os
import json

from platform_crawler.utils.utils import Util
from platform_crawler.spiders.get_login_data.wifi_key import WifiKey
from platform_crawler.spiders.pylib.task_process import TaskProcess
from platform_crawler.spiders.pylib.cut_img import cut_img


u = Util()
logger = None
url = 'http://ad.wkanx.com/#/user/login'


class WifiSpider(TaskProcess):

    def __init__(self, data, **kwargs):
        global logger
        data['platform'] = 'wifikey'
        super().__init__(user_info=data, **kwargs)
        self.init_post_data()
        self.dates = data.get('dates') if data.get('dates') else None
        self.cookie_str = None
        logger = self.logger

    def init_post_data(self):
        self.url = 'http://ad.wkanx.com/data/report/list'
        self.count = 0
        self.form_data = {
            "startDate": None,
            "endDate": None,
            "pageSize": "50",
            "order": "desc",
            "orderBy": "date",
            "dimension": "date",
            "viewLevel": "summary",
            "isHasDataOnly": "true",
            "isVideoPlayClickOnly": "false",
        }
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
            'Cookie': None,
            'Host': "ad.wkanx.com",
            'Referer': "http://ad.wkanx.com/",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
            'Cache-Control': "no-cache"
        }

    def get_balance(self):
        balance_url = 'http://ad.wkanx.com/data/account/balance-read'
        ref = 'http://ad.wkanx.com/v2/fe/home'
        res = self.deal_result(self.execute('POST', balance_url, referer=ref), json_str=True)
        if not res.get('succ'):
            raise Exception(res.get('msg'))
        balance = res.get('msg').get('result').get('balance')/100
        self.balance_data = {'账号': self.acc, '余额': balance}

    def parse_balance(self):
        headers = ['账号', '余额']
        return headers, [self.balance_data]

    def login_part(self, um):
        um['platform'] = 'wifikey'
        self.login_obj = WifiKey(um, um.get('platform'))
        self.d = self.login_obj.d
        return self.login_obj.run_login()

    def deal_login_result(self, login_res):
        if not login_res.get('succ'):
            return login_res
        self.headers.update({'User-Agent': self.user_agent})
        self.d = login_res.get('driver')
        cookies = login_res.get('cookie')
        self.cookie_str = '; '.join(['%s=%s' % (e['name'], e['value']) for e in cookies])

    def get_data_part(self, um):
        ys, ms, ye, me = self.dates if self.dates else (None, None, None, None)
        mths, dates = u.make_dates(ys=ys, ms=ms, ye=ye, me=me)
        data_list = []
        for sd, ed in dates:
            data_name = '%s_%s' % (sd, ed)
            logger.info('date range ---- %s~%s' % (sd, ed))
            # 数据
            data_res = self.get_data(sd, ed, data_name)
            if not data_res.get('succ'):
                self.login_obj.close_chrome_debugger()
                return {'succ': False}
            if data_res.get('msg') != 'no data':
                logger.info(f'date_range: {sd}~{ed} | no data')
                data_list.append(1)
        if not data_list:
            self.result_kwargs['has_data'] = 0
            self.login_obj.close_chrome_debugger()

    def get_img_part(self, get_data_res=None, **kwargs):
        # 图片
        ys, ms, ye, me = self.dates if self.dates else (None, None, None, None)
        mths, dates = u.make_dates(ys=ys, ms=ms, ye=ye, me=me)
        for sd, ed in dates:
            self.get_img(sd, ed)
        self.login_obj.close_chrome_debugger()
        return {'succ': True}

    def get_data(self, start, end, data_name):
        self.form_data['startDate'] = start
        self.form_data['endDate'] = end
        self.headers['Cookie'] = self.cookie_str
        data_list = []
        # 分页爬取
        i = 1
        while True:
            ret = self.deal_result(self.execute('POST', self.url, data=self.form_data, headers=self.headers), json_str=True)
            # ret = post(self.url, headers=self.headers, data=self.form_data)
            if not ret.get('succ'):
                return ret
            data = ret.get('msg')
            count = int(data.get('result').get('count'))
            # 页数
            if i != 1:
                self.form_data['pageNo'] = str(i)
            data_list.extend(data['result']['list'])
            if count < 50:
                break
            count -= 50
            i += 1

        if not data_list:
            return {'succ': True, 'msg': 'no data'}
        data_path = os.path.join(self.dir_path, data_name + '.json')
        data['result']['list'] = data_list
        data['result'].pop('pageNo')
        data['result'].pop('pageSize')
        logger.debug('crawled data: %s' % data)
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        return {'succ': True}

    def get_img(self, start, end):
        heads = 'http://ad.wkanx.com/#/ader/report/list?dateRange=%s,%s&order=desc&orderBy=date%s&dimension=date'
        scroll_to_top = 'var q=document.documentElement.scrollTop=0'
        get_height = 'return a=document.body.offsetHeight'
        url = heads % (start, end, '&pageNo=1')
        self.d.get(url)
        # 回到顶部
        try:
            self.d.execute_script(scroll_to_top)
        except:
            self.d.refresh()
            self.d.implicitly_wait(5)
            self.d.execute_script(scroll_to_top)
        # 获取高度
        height = self.d.execute_script(get_height) + 300
        time.sleep(3)
        pic_name = os.path.join(self.dir_path, '%s_%s.png' % (start, end))
        res = cut_img(height, self.dir_path, pic_name)
        if not res.get('succ'):
            logger.warning('got picture failed: %s' % pic_name)
        logger.info('got a picture: %s' % pic_name)
        return {'succ': True}

