"""
oppo 应用商店 zwb
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
import os
import json

from platform_crawler.utils.utils import Util
from platform_crawler.spiders.pylib.scp_client import upload_file, init_dst_dir
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.spiders.pylib.task_process import TaskProcess
from platform_crawler.spiders.get_login_data.login_oppo import Oppo
from platform_crawler.settings import join, JS_PATH, sd_path


ut = Util()
logger = None


class OppoSpider(TaskProcess):

    def __init__(self, user_info, **kwargs):
        global logger
        super().__init__(user_info=user_info, **kwargs)
        self.cookie_str = None
        self.balance_data = None
        self.oppo_msg_home_path = None
        logger = self.logger

    def get_data(self, url, sd, ed, tk, data_type, sec=False):
        """
        获取数据
        """
        # 处理文件名
        fname = '%(data_type)s_%(sd)s_%(ed)s.json' % {'data_type': data_type, 'sd': sd, 'ed': ed}
        home_path = self.dir_path if data_type != '信息流推广' else self.oppo_msg_home_path
        file_name = os.path.join(home_path, fname)
        accept = '*/*' if data_type != '信息流推广' else 'application/json, text/plain, */*'
        # 处理数据
        headers = {
            'Accept': accept,
            'Content-Type': "application/x-www-form-urlencoded",
            'Connection': 'keep-alive',
            'Cookie': self.cookie_str,
            'tk': tk,
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
        }
        range_key = 'daterange' if sec else 'dateRange'
        pay_key = 'keyWord' if sec else 'moduleId'
        payload = {range_key: '%s~%s' % (sd, ed), 'appId': '', pay_key: '', 'type': 1}
        if data_type == '信息流推广':
            payload = {'beginTime': sd.replace('-', ''), 'endTime': ed.replace('-', ''), 'page': '1', 'pageCount': '31',
                       'chnId': '2', 'timeLevel': 'DAY'}
        data = self.deal_result(self.execute('POST', url, data=payload, headers=headers), json_str=True)
        if not data.get('succ'):
            raise Exception('Net Error: %s' % data.get('msg'))
        data = data.get('msg')
        # 没有数据
        if isinstance(data.get('data'), list) and len(data.get('data')) == 0:
            return {'succ': False, 'msg': 'no data'}
        # 写入文件
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        logger.info('crawled data: --------%s' % data)
        return {'succ': True, 'data_type': data_type, 'content': data}

    def reset_ck(self):
        cookie = self.d.get_cookies()
        tk = [e.get('value') for e in cookie if e.get('name') == 'tk'][0]
        cookie = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in cookie])
        return tk, cookie

    def get_data_process(self, tk):
        # 获取时间
        dates = self.get_dates
        data_list = []
        for sd, ed in dates:
            sec = False
            url = [{'url': 'https://e.oppomobile.com/cpdStat/trend', 'data_type': '应用分发'},
                   {'url': 'https://e.oppomobile.com/searchStat/trend', 'data_type': '搜索推广'},
                   {'url': 'https://e.oppomobile.com/v2/data/Q/plan/list', 'data_type': '信息流推广'}]
            for u in url:
                # 获取数据
                data_res = self.get_data(u.get('url'), sd, ed, tk, u.get('data_type'), sec=sec)
                sec = True
                if data_res.get('succ'):
                    data_list.append(1)
                    if not self.is_get_img:     # 截图控制
                        continue
                    # 获取图片
                    self.get_img(sd, ed, data_res.pop('content'), u.get('data_type'))
                    # tk, cookie = self.reset_ck()
                elif data_res.get('msg') == 'no data':
                    continue
        if not data_list:
            self.result_kwargs['has_data'] = 0
        return {'succ': True}

    def show_data(self, data, msg=None):
        """通过js去除分页，重新展示数据部分内容"""
        # js_name = 'show_oppo_data.js' if msg else 'show_oppo_data2.js'
        js_name = 'show_oppo_data.js'
        with open(join(JS_PATH, js_name), 'r', encoding='utf-8') as f:
            data_js = f.read()
        data_js = "%s(%s, 1);" % (data_js, data)
        self.d.execute_script(data_js)

    def update_with_js(self, sd, ed):
        fname = join(JS_PATH, 'opponew.js')
        with open(fname, 'r') as f:
            js = f.read()
        self.d.execute_script(js % (sd, ed))

    def get_img(self, sd, ed, content, data_type):
        """截图操作"""
        if data_type == '信息流推广':
            self.d.get('https://e.oppomobile.com/market/report/index.html')
            for i in range(2):
                self.d.execute_script("document.querySelectorAll('.select')[0].querySelectorAll('li a')[2].click()")
            for i in range(2):
                self.d.execute_script("document.querySelectorAll('.select')[2].querySelectorAll('li a')[1].click()")
            self.update_with_js(sd.replace('-', '/'), ed.replace('-', '/'))
            self.d.execute_script('document.querySelector(".downTableBtn").click()')
        else:
            self.d.get('https://e.oppomobile.com/bid/list')
            self.d.execute_script('document.documentElement.scrollTop=0')
            self.wait_element(By.LINK_TEXT, '报表').click()      # 进入报表
            self.wait_element(By.LINK_TEXT, data_type).click()   # 选择数据类型
            # 更新日期
            self.wait_element(By.ID, 'daterange').clear()
            self.d.find_element_by_id('daterange').send_keys('%s~%s' % (sd, ed))
            self.wait_element(By.CSS_SELECTOR, '.btn-success').click()
            self.d.find_element_by_css_selector('body').click()
            # self.d.execute_script("document.querySelector('.btn-success').click()")
            # 清空原数据，手动展示数据
            data_type = '应用分发' if data_type == '应用分发' else None
            self.show_data(content, msg=data_type)

        # 截图
        self.d.execute_script('document.documentElement.scrollTop=0')
        hjs = 'return h = document.body.offsetHeight'
        height = self.d.execute_script(hjs)
        pic_name = '%(data_type)s_%(sd)s_%(ed)s.png' % {'data_type': data_type, 'sd': sd, 'ed': ed}
        home_path = self.oppo_msg_home_path if data_type == '信息流推广' else self.dir_path
        cut_res = cut_img(height, home_path, pic_name)
        if not cut_res['succ']:
            logger.error('get img %s failed-------msg: %s' % (pic_name, cut_res.get('msg')))
            raise Exception('Cut img error:\npic_name:%s\ncut_result_msg:%s' % (pic_name, cut_res.get('msg')))
        logger.info('height: %s ---picname: %s' % (height, pic_name))
        if data_type != '信息流推广':
            self.d.get('https://e.oppomobile.com/searchStat/index')
        return cut_res

    def login_and_get_data(self, ui):
        # 登陆
        # """
        lo = Oppo(ui, '%s.login' % ui.get('platform'))
        login_res = lo.run_login()
        if not login_res.get('succ'):
            self.d.quit()
            return login_res
        self.d = login_res.get('driver')
        self.wait = WebDriverWait(self.d, 20)
        cookies = login_res.get('cookies')
        tk = 'null'
        self.cookie_str = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in cookies])
        # """
        # cookies =
        # 获取数据
        err_list = self.get_data_process(tk)
        if not err_list.get('succ'):
            self.d.quit()
            return {'succ': False, 'msg': err_list.get('msg')}
        logger.error(err_list.get('msg'))
        self.d.quit()
        return {'succ': True}

    def get_balance(self) -> None:
        url = 'https://e.oppomobile.com/v2/communal/owner/balance'
        headers = {
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        }
        self._headers.update(headers)
        res = self.deal_result(self.execute('POST', url), json_str=True)
        if not res.get('succ'):
            raise Exception('Balance data got failed!')
        if res.get('msg').get('code') != 0:
            raise Exception('Balance data got failed!')
        self.balance_data = res.get('msg').get('data')

    def parse_balance(self):
        # data = {'账号': self.acc, '余额': self.balance_data.get('cashBal', 0)}
        headers = ['账号', '余额']
        return headers, self.balance_data.get('cashBal', 0)

    def run(self, ui):
        # 创建文件夹
        cutime = time.strftime('%Y-%m-%d')
        dir_name = '%(taskId)s_%(cTime)s_%(account)s' % {'taskId': ui['id'], 'cTime': time.strftime('%Y-%m-%d_%H-%M-%S'), 'account': self.acc}
        self.dir_path = join(sd_path, ui['platform'], cutime, dir_name)
        msg_platform = 'OPPOXXL'
        self.oppo_msg_home_path = join(sd_path, msg_platform, cutime, dir_name)
        os.makedirs(self.dir_path)
        os.makedirs(self.oppo_msg_home_path)
        err_img_name = join(self.dir_path, 'error_%s_%s.jpg' % (int(time.time()), ui.get('flag')))
        # get data part
        try:
            res = self.login_and_get_data(ui)
            if not res.get('succ'):
                self.save_screen_shot(err_img_name)
                return res
        except Exception as er:
            self.save_screen_shot(err_img_name)
            logger.error(er, exc_info=1)
            return {'succ': False, 'msg': 'got unKnown error'}

        # 检测是否有图片
        pics = [x for x in os.listdir(self.dir_path) if 'png' in x]
        if len(pics) == 0:
            self.result_kwargs['has_pic'] = 0
        dst_data_path = '/data/python/%s/%s/%s' % (ui.get('platform'), cutime, dir_name)
        if self.is_cpa:
            dst_data_path = '/data/python/%s/%s/%s/%s' % ('CPA', ui.get('platform'), cutime, dir_name)
        # 上传
        if not upload_file(self.dir_path, ui.get('platform')):
            return {'succ': False, 'msg': 'upload failed'}
        init_dst_dir(msg_platform)
        if not upload_file(self.oppo_msg_home_path, msg_platform):
            return {'succ': False, 'msg': 'upload failed'}
        # post
        return {'succ': True, 'data_path': dst_data_path}

