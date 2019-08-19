"""
百度手机助手 zwb
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
import os
import json

from platform_crawler.utils.utils import Util
from platform_crawler.utils.post_get import post
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.spiders.get_login_data.login_baidu_phone_helper import BaiDuPhone
from platform_crawler.spiders.pylib.task_process import TaskProcess
from platform_crawler.settings import join, JS_PATH


u = Util()
logger = None


class BaiduPhoneSpider(TaskProcess):

    def __init__(self, user_info, **kwargs):
        global logger
        super().__init__( user_info=user_info, **kwargs)
        logger = self.logger
        self.cookie_str = None

    def get_data(self, sd, ed):
        """
        获取数据
        """
        url = "http://baitong.baidu.com/request.ajax?path=appads/GET/report/all/list"
        # 处理文件名
        fname = '%s_%s.json' % (sd, ed)
        file_name = os.path.join(self.dir_path, fname)
        # 处理数据
        headers = {
            'Accept': "*/*",
            'Content-Type': "application/x-www-form-urlencoded",
            'Cookie': self.cookie_str,
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
        }
        p = {"startDate": sd, "endDate": ed, "pageSize": 50, "page": 1, "sortField": "date", "sortOrder": "desc", "timeUnit": 1}
        payload = {'params': json.dumps(p)}
        data = post(url, data=payload, headers=headers)
        if not data.get('is_success'):
            return {'succ': False, 'msg': 'net error'}
        data = data.get('msg').content.decode('utf-8')
        # 没有数据
        if json.loads(data).get('data').get('count') == 0:
            logger.info({'msg': 'no data', 'date': '%s-%s' % (sd, ed)})
            return {'succ': False, 'msg': 'no data'}
        # 写入文件
        with open(file_name, 'w', encoding='utf-8') as f:
            try:
                f.write(data)
            except Exception as e:
                logger.error(e, exc_info=1)
        logger.info('crawled data: --------%s' % data)
        return {'succ': True}

    def update_date(self, sd, ed):
        """更新日期"""
        with open(join(JS_PATH, 'baidu_baitong.js'), 'r', encoding='utf-8') as f:
            date_js = f.read()
        self.d.execute_script(date_js % (sd, ed))

    def get_data_process(self):
        # 清除遮挡物
        try:
            self.wait_element(By.CLASS_NAME, 'ui-title-window', wait_time=3)
            self.d.execute_script('document.querySelector(".ui-title-window").remove()')
        except:
            logger.debug('没有遮挡物出现，pass')
        # 跳转目标页(数据报表)
        self.wait_element(By.XPATH, '//div[@class="sys-menu-item"][2]').click()
        # 获取时间
        mths, dates = u.make_dates(ms=None, ys=None, ye=None, me=None)
        err_list = []
        for sd, ed in dates:
            # 获取数据
            data_res = self.get_data(sd, ed)
            if data_res.get('succ'):
                # 截图流程
                img_res = self.img_process(sd, ed)
                err_list.append(img_res)
            elif data_res.get('msg') != 'no data':
                err_list.append(1)
        if len(err_list) == 0:
            self.result_kwargs['has_data'] = 0
        return {'succ': True}

    def img_process(self, sd, ed):
        self.d.refresh()
        self.d.execute_script('document.documentElement.scrollTop=0')
        self.wait_element(By.CSS_SELECTOR, '.el-pagination i').click()
        time.sleep(2)
        # 选择单页条数
        items = self.d.find_elements_by_css_selector('.el-scrollbar span')
        for i in items:
            if i.text[:2] == '50':
                i.click()
        # 更新日期
        self.update_date(sd, ed)
        # 获取图片
        return self.get_img(sd, ed)

    def get_img(self, sd, ed):
        """截图操作"""
        hjs = 'return h = document.body.offsetHeight'
        height = self.d.execute_script(hjs)
        pic_name = '%s_%s.png' % (sd, ed)
        cut_res = cut_img(height, self.dir_path, pic_name)
        if not cut_res['succ']:
            logger.error('get img %s failed-------msg: %s' % (pic_name, cut_res.get('msg')))
        logger.info('height: %s ---picname: %s' % (height, pic_name))
        return cut_res

    def parse_balance(self):
        url = 'http://baitong.baidu.com/request.ajax?path=appads/GET/overview/index/finance'
        headers = {
            'Accept': "*/*",
            'Content-Type': "application/x-www-form-urlencoded",
            'Cookie': self.cookie_str,
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
        }
        payload = {'path': 'appads/GET/overview/index/finance'}
        res = self.deal_result(self.execute('POST', url, data=payload, headers=headers), json_str=True)
        if not res.get('succ'):
            raise Exception(res.get('msg'))
        data = res.get('msg').get('data')
        balance = float(data.get('chunhua').get('balance'))
        headers = ['账号', '余额']
        balance = [{'账号': self.acc, '余额': balance}]
        logger.info(balance)
        return headers, balance

    def login_part(self, ui):
        self.login_obj = BaiDuPhone(ui, ui.get('platform'))
        return self.login_obj.run_login()

    def deal_login_result(self, login_res):
        if not login_res.get('succ'):
            return login_res
        self.d = login_res.get('driver')
        self.wait = WebDriverWait(self.d, 20)
        cookies = login_res.get('cookies')
        self.cookie_str = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in cookies])

    def get_data_part(self, ui, **kwargs):
        # """
        # cookies =
        # 获取数据
        try:
            self.wait_element(By.CLASS_NAME, 'ui-title-window')
            self.d.execute_script("document.querySelector('.ui-title-window').remove()")
        except:
            pass
        err_list = self.get_data_process()
        logger.error(err_list)
        return err_list
