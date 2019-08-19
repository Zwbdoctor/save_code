from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as EC
from requests.utils import quote

from platform_crawler.utils.post_get import post, get
from platform_crawler.utils.utils import Util
from platform_crawler.spiders.pylib.login_qq import LoginQQ
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.spiders.pylib.task_process import TaskProcess
from platform_crawler.settings import join, JS_PATH

import time
import json
import os


set_start_time = """
(function(st, et){
    if(jQuery('#daterange') && 
        jQuery('#daterange').data('daterangepicker') && 
        ('setStartDate' in jQuery('#daterange').data('daterangepicker'))
    ) {
        jQuery('#daterange').data('daterangepicker').setStartDate(st);
        jQuery('#daterange').data('daterangepicker').setEndDate(et);
        document.querySelector('.applyBtn').click();

    } else {
        let settime = Date.now();
        localStorage.setItem('list_sdate', '{"data":"'+st+'","_time":'+settime+',"_expire":31308148}');
        localStorage.setItem('list_edate', '{"data":"'+et+'","_time":'+settime+',"_expire":31308148}');
    }
})('%s', '%s');"""

u = Util()
logger = None

page_version = 'old'
base_header = {
    'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'Content-Type': "application/x-www-form-urlencoded",
    'cookie': None,
    'origin': "https://e.qq.com",
    'referer': None,
    'Cache-Control': "no-cache",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
}


class AppTreasureHL(TaskProcess):

    def __init__(self, user_info, **kwargs):
        global logger
        self.dates = None
        self.cookies_str = None
        self.gtk = None
        self.uid = None
        self.init__post_param()
        self.login_obj = None
        super().__init__(headers=base_header, user_info=user_info, **kwargs)
        logger = self.logger

    def init__post_param(self):
        self.params = {
            "mod": "report", "act": "productdetail", "g_tk": None
        }
        self.pdata = {
            "page": "1", "pagesize": "50", "sdate": None, "edate": None, "product_type": "20",
            "product_id": None, "time_rpt": "0", "owner": None
        }

    def get_product(self, sd, ed):
        url = 'https://e.qq.com/ec/api.php'
        params = {'mod': 'report', 'act': 'getproduct', 'g_tk': str(self.gtk), 'sdate': sd, 'edate': ed, 'searchtype': 'product', 'product_type': '20'}
        headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
                   'referer': 'https://e.qq.com/atlas/%s/report/producttype' % self.uid,
                   'cookie': self.cookies_str,
                   'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"}
        res = get(url, params=params, headers=headers)
        if not res.get('is_success'):
            logger.error(res.get('msg').json())
        data = res.get('msg').json()
        total_num = data.get('data').get('conf').get('totalnum')
        if total_num == 0:
            return {'succ': False, 'msg': 'no data'}
        data_list = data.get('data').get('list')
        data = [{'pname': e.get('pname'), 'pid': e.get('product_id'), 'cost': e.get('cost')} for e in data_list]
        return {'succ': True, 'msg': data}

    def get_img(self, p_list, sd, ed):
        """截图，并处理图片文件"""
        with open(join(JS_PATH, 'e_qq_pagenum.js'), 'r') as p:
            pjs = p.read()
        for e in p_list:
            if not e.get('has_data'):
                continue
            picname = '%(productId)s_%(productName)s_%(sd)s_%(ed)s.png' % {
                'productId': e.get('pid'), 'productName': e.get('pname'), 'sd': sd, 'ed': ed
            }
            url = 'https://e.qq.com/atlas/%s/report/order?ptype=20&pid=%s&pname=%s' % (self.uid, e.get('pid'), quote(e.get('pname')))
            self.d.get(url)
            time.sleep(0.5)
            if page_version == 'new':   # 版本判断
                try:
                    self.wait_element(By.CLASS_NAME, 'button-more').click()
                except:
                    self.d.execute_script("document.querySelector('.button-more').click()")
            else:
                self.wait_element(By.LINK_TEXT, '查看报表', ec=EC.presence_of_element_located).click()
            time.sleep(2)

            # if page_version != 'new':
            #     u.pag.hotkey('ctrl', '-', interval=0.3)
            # 调整分页数量
            self.d.execute_script(pjs)
            time.sleep(1.5)
            self.d.switch_to.frame(self.d.find_element_by_css_selector('.splitview-tabs-body iframe'))
            # 获取高度
            get_height = 'return a=document.querySelector("#content").offsetHeight'
            height = self.d.execute_script(get_height)
            # 截图
            cut_res = cut_img(height, self.dir_path, picname)
            if not cut_res['succ']:
                logger.error('get img %s_%s failed-------msg: %s' % (e['pid'], e['pname'], cut_res['msg']))
            logger.info('height: %s ---picname: %s' % (height, picname))
            # 恢复
            # u.pag.hotkey('ctrl', '0', interval=0.3)
        else:
            return {'succ': True}

    def get_data_process(self, dates):
        # 获取上个月到现在每天的数据
        err_list, res, data_list, has_data_in_two_mth = [], None, [], []
        for sd, ed in dates:
            p_res = self.get_product(sd, ed)
            if not p_res.get('succ') and p_res.get('msg') == 'no data':
                continue
            p_list = p_res.get('msg')
            for p in p_list:
                if page_version == 'new':
                    res = self.get_data_another_version(p, sd, ed)
                else:
                    res = self.get_data(p, sd, ed)
                if res.get('succ'):
                    time.sleep(0.2)
                    p.update({'has_data': True})
                    has_data_in_two_mth.append(1)
                    continue
                elif not res['succ'] and res.get('msg') == 'no data':
                    p.update({'has_data': False})
                else:
                    err_list.append(p)
            else:
                data_list.append({'data': p_list, 'date': [sd, ed]})
        if not has_data_in_two_mth:
            self.result_kwargs['has_data'] = 0
        return data_list

    def get_version(self):
        # 判断界面版本
        global page_version
        self.d.get('https://e.qq.com/atlas/%s/report/producttype' % self.uid)
        # if u.wait_element(self.d, (By.CLASS_NAME, 'datechoose'), 10):
        try:
            self.d.find_element_by_xpath('//div[@class="datechoose l"]')
        except:
            page_version = 'new'
        time.sleep(1)

    def get_data_another_version(self, data, sd, ed):
        logger.info('get into (self.get_data_another_version)function')
        fname = '%(productId)s_%(productName)s_%(sd)s_%(ed)s.json' % {
            'productId': data.get('pid'), 'productName': data.get('pname'), 'sd': sd, 'ed': ed
        }
        url = "https://e.qq.com/ec/api.php"
        params = {"g_tk": str(self.gtk), "product_id": data.get('pid'), "product_type": '20', "sdate": sd, "edate": ed}
        headers = {
            "cookie": self.cookies_str,
            "referer": "http://e.qq.com/atlas/%(uid)s/report/analytic2?product_id=%(pid)s&product_type=%(ptype)s" % {
                'uid': self.uid, 'pid': data.get('pid'), 'ptype': '20'
            }
        }
        self.params.update(params)
        self._headers.update(headers)
        data = get(url, params=self.params, headers=self._headers)
        if not data['is_success']:
            return {'succ': False, 'msg': data['msg']}
        file_name = os.path.join(self.dir_path, fname)
        data = json.loads(data['msg'].content.decode('utf-8'))
        cost = data.get('data').get('total').get('cost').replace(',', '')
        if float(cost) == 0:
            return {'succ': False, 'msg': 'no data'}
        data['account'] = self.acc
        with open(file_name, 'w') as f:
            json.dump(data, f)
        logger.info('crawled data: ' + json.dumps(data))
        return {'succ': True}

    def get_data(self, data, sd, ed):
        logger.info('get into (self.get_data_common_version)function')
        url = "https://e.qq.com/ec/api.php"
        fname = '%(productId)s_%(productName)s_%(sd)s_%(ed)s.json' % {
            'productId': data['pid'], 'productName': data['pname'], 'sd': sd, 'ed': ed
        }
        params = {"g_tk": str(self.gtk)}
        pdata = {
            "sdate": sd, "edate": ed, "product_type": '20',
            "product_id": data.get('pid'), "owner": self.uid
        }
        headers = {
            "cookie": self.cookies_str,
            "referer": "http://e.qq.com/atlas/%(uid)s/report/order_old?pid=%(pid)s&ptype=%(ptype)s" % {
                'uid': self.uid, 'pid': data.get('pid'), 'ptype': '20'
            }
        }
        self.params.update(params)
        self.pdata.update(pdata)
        self._headers.update(headers)
        data = post(url, data=self.pdata, params=self.params, headers=self._headers)
        if not data['is_success']:
            return {'succ': False, 'msg': data['msg']}
        file_name = os.path.join(self.dir_path, fname)
        data = json.loads(data['msg'].content.decode('utf-8'))
        cost = data.get('data').get('total').get('cost').replace(',', '')
        if float(cost) == 0:
            return {'succ': False, 'msg': 'no data'}
        data['account'] = self.acc
        with open(file_name, 'w') as f:
            json.dump(data, f)
        logger.info('crawled data: ' + json.dumps(data))
        return {'succ': True}

    def parse_balance(self, *args, **kwargs):
        # parse
        res = self.login_obj.get_balance(self.uid)
        if not res.get('succ'):
            return res
        unknown_account_name_type = {}
        balance_data = {'现金账户': 0, '虚拟账户': 0, '信用账户': 0, '换量账户': 0}
        accounts = res.get('msg')
        keys = balance_data.keys()
        for i in accounts:
            account_name = i.get('account_name')
            if account_name in keys:
                balance_data[account_name] = round(i.get('balance')/100, 2)
            else:
                # unknown_account_name_type[account_name] = round(i.get('balance')/100, 2)
                continue
        header = ['账号', '现金账户', '虚拟账户', '信用账户', '换量账户', '总计']
        balance_data['总计'] = sum(balance_data.values())
        balance_data['账号'] = self.acc
        if unknown_account_name_type:
            header.extend(unknown_account_name_type.keys())
            balance_data.update(unknown_account_name_type)
        return header, [balance_data]

    def login_part(self, ui):
        # 登陆
        self.login_obj = LoginQQ(ui, ui.get('platform'))
        return self.login_obj.run_login()

    def deal_login_result(self, login_res):
        if not login_res['succ']:
            return login_res
        if login_res.get('msg') == 'unknown situation':
            logger.warning('got unknown login situation: %s' % login_res.get('desc'))
            self.result_kwargs['has_data'] = 0
            return {'succ': True, 'msg': 'pass'}

        # 获取登录后浏览器驱动和数据
        self.d = login_res.pop('driver')
        self.cookies_str = self.login_obj.cookies.get('cookie_str')
        self.gtk = self.login_obj.gtk
        self.uid = login_res.get('data').get('uid')

        self.get_version()

    def get_data_part(self, ui, **kwargs):
        # 获取时间
        self.dates = ui.get('dates')
        ys, ms, ye, me = self.dates if self.dates else (None, None, None, None)
        mths, dates = u.make_dates(ys=ys, ms=ms, ye=ye, me=me)
        # 获取数据
        return self.get_data_process(dates)

    def get_img_part(self, get_data_res=None, **kwargs):
        # 截图
        for e in get_data_res:
            sd, ed = e.get('date')
            self.d.execute_script(set_start_time % (sd, ed))        # 更新日期
            self.d.refresh()
            self.get_img(e.get('data'), sd, ed)

        if not get_data_res:
            self.result_kwargs['has_data'] = 0
        return {'succ': True}
