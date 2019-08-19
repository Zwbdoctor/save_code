'''
百度信息流 zly
'''
from platform_crawler.utils.utils import Util
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.spiders.get_login_data.login_baidu_message_stream import BaiDuMessage
from platform_crawler.spiders.pylib.task_process import TaskProcess
from platform_crawler.settings import join, JS_PATH

import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from requests.utils import quote
import time
import os

u = Util()
logger = None


class BaiduMessageSpider(TaskProcess):

    def __init__(self, user_info, **kwargs):
        global logger
        super().__init__(user_info=user_info, **kwargs)
        logger = self.logger
        self.cookie_list = None
        self.cookie_str = None

    def set_date(self, sd, ed):
        """更新起止日期"""
        with open(join(JS_PATH, 'baidu_message_stream.js'), 'r',
                  encoding='utf-8') as f:  # 相对于当前文件路径写法
            setDateJs = f.read()
            setDateJs = setDateJs % {'datest': sd, 'dateet': ed}
            self.d.execute_script(setDateJs)

    def extractDataFromCookie(self):
        self.userid = ''
        self.token = ''
        for e in self.cookie_list:
            if e.get('name') == '__cas__id__3':
                self.userid = e.get('value')
            if e.get('name') == '__cas__st__3':
                self.token = e.get('value')

    def get_img(self, dates=None):
        """截图，并处理图片文件"""
        try:
            self.d.implicitly_wait(3)
            self.d.find_element_by_id('close-btn').click()
        except Exception:
            pass
        self.wait_element(By.CSS_SELECTOR, '.feed-report-tableArea .tr-data')
        try:
            for sd, ed in dates:
                self.d.refresh()
                self.wait_element(By.CSS_SELECTOR, '.feed-report-tableArea .tr-data')
                # 更新日期
                self.set_date(sd, ed)
                time.sleep(1)
                # 等待数据表,无数据也会有tr-data
                self.wait_element(By.CSS_SELECTOR, '.feed-report-tableArea .tr-data')
                # 截图
                pic_name = '%s_%s.png' % (sd, ed)
                height = self.d.execute_script(r'return document.body.offsetHeight')
                cut_res = cut_img(height, self.dir_path, pic_name)
                if not cut_res['succ']:
                    logger.error(
                        'cut picture failed, possible msg:\ndir_path:%s\npic_name: %s' % (self.dir_path, pic_name))
                logger.info('got a picture: pic_msg: %s' % os.path.join(self.dir_path, pic_name))
                time.sleep(2)
            else:
                return {'succ': True, 'msg': 'img got success'}
        except Exception as e:
            logger.error(e, exc_info=1)
            return {'succ': False, 'msg': e}

    def get_data(self, osd, oed):
        url = "http://feedads.baidu.com/nirvana/request.ajax"
        querystring = {"path": "pluto/GET/mars/reportdata"}
        pdata = {
            "userid": self.userid,
            "token": self.token,
            "path": quote("pluto/GET/mars/reportdata", safe=''),
            "params": quote(json.dumps({"pageSize": 50, "pageNo": 1, "maxRecordNum": 0,
                                  "reportinfo": {"reportid": 0, "starttime": osd, "endtime": oed, "isrelativetime": 0,
                                                 "relativetime": 14, "mtldim": 2, "idset": self.userid, "mtllevel": 200,
                                                 "platform": 23, "reporttype": 700, "splitDim": "", "filter": None,
                                                 "dataitem": "date,useracct,paysum,shows,clks,clkrate,avgprice,showpay,mmpv,trans",
                                                 "reporttag": 0, "reportcycle": 1, "timedim": 7, "firstday": 1,
                                                 "ismail": 0, "mailaddr": "", "sortlist": "date DESC",
                                                 "reportname": "信息流推广账户报告", "userid": self.userid, "reportlevel": 100,
                                                 "rgtag": None, "mtag": None, "feedSubject": "", "bstype": ""}}))
        }
        pdata = '&'.join('%s=%s' % (k, v) for k, v in pdata.items())
        headers = {
            'Accept': "*/*",
            'Content-Type': "application/x-www-form-urlencoded",
            'Cookie': self.cookie_str,
            'Host': "feedads.baidu.com",
            'Referer': "http://feedads.baidu.com/nirvana/main.html?userid=%s" % self.userid,
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
        }
        data = self.deal_result(self.execute('POST', url, params=querystring, data=pdata, headers=headers), json_str=True)
        if not data['succ']:
            raise Exception(data.get('msg'))
        file_name = os.path.join(self.dir_path, '%s_%s.json' % (osd, oed))
        tmp = data['msg']
        if (not tmp) or (not tmp.get('data')) or (tmp['data']['totalCount'] == 0):
            return {'succ': True, 'msg': 'no data'}

        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(data)
        logger.info('crawled data: ' + data)
        return {'succ': True}

    def parse_balance(self):
        data = [{'账号': self.acc, '余额': float(self.balance_data)}]
        logger.info(data)
        header = ['账号', '余额']
        return header, data

    def login_part(self, ui):
        self.login_obj = BaiDuMessage(ui, ui.get('platform'))
        return self.login_obj.run()

    def ensure_proto(self):
        JS = """
        bo = document.querySelectorAll('%s');
        if(bo && bo.length>0){
            bo[0].click();
        }
        """
        self.d.execute_script(JS % '#license-input-agreement')
        time.sleep(1)
        self.d.execute_script(JS % '.input-btn-blue')

    def deal_login_result(self, login_res):
        if not login_res['succ']:
            return login_res

        # 获取登录后浏览器驱动和数据
        self.d = login_res.pop('driver')
        self.ensure_proto()
        self.balance_data = self.d.find_element_by_class_name('info-a-value').text.strip()
        self.wait = WebDriverWait(self.d, 20)
        self.cookie_list = login_res.get('cookies')

        # 从cookie中获取请求参数
        self.extractDataFromCookie()
        if not self.userid:
            logger.error('baidu_message_stream no userid cookie %s', self.cookie_list)
        self.d.get('http://feedads.baidu.com/nirvana/main.html?userid=%s#/feed/report~page=accountReport' % self.userid)
        time.sleep(2)
        self.cookie_list = self.d.get_cookies()
        self.cookie_str = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in self.cookie_list])

    def get_img_part(self, **kwargs):
        # 获取时间
        days = self.get_dates
        # 截图操作
        img_res = self.get_img(dates=days)
        if not img_res.get('succ'):
            return img_res
        self.d.quit()

    def get_data_part(self, ui, **kwargs):
        days = self.get_dates
        # 获取上个月到现在每天的数据
        err_list, data_list = [], []
        for start_date, end_date in days:
            res = self.get_data(start_date, end_date)
            if res.get('msg') == 'no data':
                continue
            if not res['succ']:
                raise Exception(f'start: {start_date}| end: {end_date} | got data failed')
            data_list.append(1)
            time.sleep(0.25)
        if not data_list:
            self.result_kwargs['has_data'] = 0
        return {'succ': True}
