"""
快手 url: https://ad.e.kuaishou.com/#/welcome?redirectUrl=https%3A%2F%2Fad.e.kuaishou.com%2F%23%2Findex
author: Zavier
"""
import time
import json
import os
from platform_crawler.spiders.pylib.task_process import TaskProcess
from platform_crawler.spiders.pylib.cut_img import cut_img

logger = None


class LoginKuaiShou:

    def __init__(self, user_info):
        self.user = user_info.get('account')
        self.pwd = user_info.get('password')
        self.spider = None
        self.d = None
        ...

    def is_login(self):
        cookie_list = self.d.get_cookies()
        cookie_keys = '; '.join([x.get('name') for x in cookie_list])
        if 'kuaishou.ad.dsp_ph' in cookie_keys:
            cookies_str = '; '.join(['%s=%s' % (x.get('name'), x.get('value')) for x in cookie_list])
            dsp_ph = 0
            for x in cookie_list:
                if x.get('name') == 'kuaishou.ad.dsp_ph':
                    dsp_ph = x.get('value')
                    break
            return {'status': 0, 'data': cookies_str, 'dsp_ph': dsp_ph}
        return {'status': 1, 'err_msg': 'Login Failed!'}

    def login(self):
        url = 'https://ad.e.kuaishou.com/#/welcome?redirectUrl=https%3A%2F%2Fad.e.kuaishou.com%2F%23%2Findex'
        self.d.get(url)
        self.d.implicitly_wait(3)
        self.d.find_element_by_css_selector('.phone input').send_keys(self.user)
        self.d.find_element_by_css_selector('.password input').send_keys(self.pwd)
        self.d.find_element_by_css_selector('div.foot').click()
        # self.d.find_element_by_css_selector('.dsp-menu .add')
        time.sleep(1)
        try:
            self.d.find_element_by_css_selector('.phone input')
            print('未登录成功')
        except:
            pass        # 未登录，出现未知错误
        res = self.is_login()
        if res.get('status') != 0:
            logger.error('Login Failed')
            err_msg = self.d.find_element_by_css_selector('.tip').text
            logger.error('Error Desc: %s' % err_msg)
            res.update({'succ': False, 'msg': res.get('err_msg'), 'invalid_account': True})
            return res
        res['succ'] = True
        logger.info('Login Success!')
        return res

    def run_login(self, spider_obj):
        self.spider = spider_obj
        self.d = self.spider.d
        return self.login()


class KuaiShouSpider(TaskProcess):

    def __init__(self, user_info, **kwargs):
        global logger
        super().__init__(user_info=user_info, **kwargs)
        logger = self.logger
        self._cookies_str = None
        self.dsp = None

    def login_part(self, *args, **kwargs):
        ks = LoginKuaiShou(self.user_info)
        self.init_browser()
        return ks.run_login(self)

    def deal_login_result(self, login_res):
        if not login_res.get('succ'):
            return login_res
        self._cookies_str = login_res.get('data')
        self.dsp = login_res.get('dsp_ph')

    def get_balance(self):
        url = 'https://ad.e.kuaishou.com/rest/dsp/hitLine/account'
        headers = {
            "Accept": "application/json",
            "Cookie": self._cookies_str,
            "Host": "ad.e.kuaishou.com",
            "Referer": "https://ad.e.kuaishou.com/?refreshToken=false",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"
        }
        result = self.deal_result(self.execute('GET', url, headers=headers), json_str=True)
        if not result.get('succ'):
            return result
        self.balance_data = result.get('msg')

    def parse_balance(self):
        balance = self.balance_data.get('data').get('banlance') / 1000
        logger.info(f'Got balance data: {balance}')
        headers = ['账号', '账户余额']
        # data = [{'账号': self.acc, '账户余额': balance}]
        return headers, balance

    def get_data_part(self, *args, **kwargs):
        dates = self.get_dates
        has_data = []
        for sd, ed in dates:
            status = self.get_data(sd, ed)
            if status.get('status') == 2:
                has_data.append(sd)
        if not has_data:
            self.result_kwargs['has_data'] = 0

    def get_data(self, sd, ed):
        url = f"https://ad.e.kuaishou.com/rest/dsp/report/effect/detailedReport?kuaishou.ad.dsp_ph={self.dsp}"
        headers = {
            'Accept': "application/json",
            'Content-Type': "application/json;charset=UTF-8",
            'Cookie': self._cookies_str,
            'Host': "ad.e.kuaishou.com",
            'Referer': "https://ad.e.kuaishou.com/?refreshToken=false",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36",
        }
        st = time.mktime(time.strptime(sd, '%Y-%m-%d'))
        et = time.mktime(time.strptime(ed, '%Y-%m-%d'))
        payload = {"viewType": 1, "startTime": int(st)*1000, "endTime": int(et)*1000, "groupType": 1,
                   "campaignType": -1, "idSet": [], "sortingColumn": "", "order": 0,
                   "pageInfo": {"totalCount": 0, "pageSize": 40, "currentPage": 1}}
        result = self.deal_result(self.execute('POST', url, data=json.dumps(payload), headers=headers), json_str=True)
        if not result.get('succ'):
            raise Exception(result.get('msg'))
        data = result.get('msg')
        if not data.get('resultList'):
            logger.info(f'Date Range: {sd}~{ed}|Msg: No Data!')
            return {'status': 2, 'err_msg': 'no data'}
        logger.info(f'Date Range: {sd}~{ed}|Data: {data}')
        file_name = os.path.join(self.dir_path, '%s_%s.json' % (sd, ed))
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        return {'status': 0}

    def get_img_part(self, *args, **kwargs):
        dates = self.get_dates
        for sd, ed in dates:
            self.get_img(sd, ed)

    def get_img(self, sd, ed):
        ch = lambda x: int(time.mktime(time.strptime(x, '%Y-%m-%d')))*1000
        url = f"https://ad.e.kuaishou.com/?refreshToken=false#/report/effect/account?startTime={ch(sd)}&endTime={ch(ed)}"
        self.d.get(url)
        self.d.find_element_by_css_selector('.ant-pagination .ant-select-selection__rendered').click()  # 等待页面刷新出元素后继续
        # 选择页面展现数量
        self.d.execute_script("""document.querySelectorAll('li[role="option"]')[1].click()""")
        time.sleep(2)
        # 截图
        height = self.d.execute_script('return a=document.documentElement.offsetHeight')
        picname = f'{sd}_{ed}.png'
        cut_res = cut_img(height, self.dir_path, picname)
        if not cut_res.get('succ'):
            logger.error('got pic failed  ---  pic_name: %s' % picname)
        logger.info('got an pic: %s' % picname)




