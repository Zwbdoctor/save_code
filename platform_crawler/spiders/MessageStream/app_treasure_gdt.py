"""
应用宝换量 zwb
"""
from platform_crawler.utils.post_get import post, get
from platform_crawler.utils.utils import Util
from platform_crawler.spiders.pylib.login_qq import LoginQQ
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.spiders.pylib.task_process import TaskProcess
from platform_crawler.settings import join, JS_PATH

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import json
import time
import os

u = Util()
logger = None
page_version = 'old'
base_header = {
    'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'Content-Type': "application/x-www-form-urlencoded",
    'cookie': None,
    'origin': "https://e.qq.com",
    'referer': None,
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
}


class AppTreasureGDT(TaskProcess):

    def __init__(self, user_info, **kwargs):
        global logger
        self.cookie_str = None
        self.cookie = None
        self.g_tk = None
        self.uid = None
        self.dates = None
        self.init__post_param()
        super().__init__(headers=base_header, user_info=user_info, **kwargs)
        logger = self.logger

    def init__post_param(self):
        self.params = {
            "mod": "report", "act": "productdetail", "g_tk": None
        }
        self.pdata = {
            "page": "1", "pagesize": "50", "sdate": None, "edate": None, "product_type": None,
            "product_id": None, "owner": None, 'g_tk': None
        }

    def get_img(self, data, sd, ed):
        # 跳转数据报表页面
        url = 'https://e.qq.com/atlas/%(uid)s/report/order?ptype=%(tid)s&pid=%(pid)s&pname=%(pn)s' % {
            'uid': self.uid, 'tid': data.get('type_id'), 'pid': data.get('pdata').get('pid'),
            'pn': data.get('pdata').get('pname')
        }
        self.d.get(url)
        pic_name = '%(ptype)s_%(productId)s_%(productName)s_%(sd)s_%(ed)s.png' % {
            'ptype': data.get('tname'), 'productId': data.get('pdata').get('pid'),
            'productName': data.get('pdata').get('pname'), 'sd': sd, 'ed': ed
        }  # 图片命名
        time.sleep(3)
        try:
            self.wait_element(By.LINK_TEXT, '查看报表', wait_time=6).click()
        except:
            self.d.execute_script('document.querySelector(".button-more").click()')
            # self.wait_element(By.CLASS_NAME, 'button-more').click()
        time.sleep(1)
        # 调整分页数量
        with open(join(JS_PATH, 'e_qq_pagenum.js'), 'r') as p:
            pjs = p.read()
        self.d.execute_script(pjs)
        time.sleep(1.5)
        self.d.switch_to.frame(self.d.find_element_by_css_selector('.splitview-tabs-body iframe'))
        # 获取高度
        get_height = 'return a=document.querySelector("#content").offsetHeight'
        height = self.d.execute_script(get_height)
        cut_res = cut_img(height, self.dir_path, pic_name)
        if not cut_res['succ']:
            logger.error(
                'get img %s_%s failed-------msg: %s' % (data.get('tname'), data.get('pdata')[1], cut_res['msg']))
        logger.info('height: %s ---picname: %s' % (height, pic_name))
        time.sleep(1)
        logger.info('got an img: picname--%s' % pic_name)

    def get_type_ids(self):
        """获取类型id"""
        url = 'https://e.qq.com/ec/api.php'
        querystring = {"mod": "product", "act": "getproducttypelist", "g_tk": self.g_tk, "owner": self.uid}
        headers = {
            'accept': "application/json, text/javascript, */*; q=0.01",
            'cookie': self.cookie_str,
            'referer': "https://e.qq.com/atlas/%s/report/producttype" % self.uid,
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3569.0 Safari/537.36"
        }
        res = get(url, params=querystring, headers=headers)
        if not res.get('is_success'):
            return {'succ': False, 'msg': res.get('msg')}
        data = res.get('msg').json()
        ids = [(x.get('id'), x.get('name')) for x in data.get('data')]
        return {'succ': True, 'msg': ids}

    def get_data_another_version(self, sd, ed, data, tid, tname):
        logger.info('get into (self.get_data_another_version)function')
        # 文件名
        fname = '%(productType)s_%(productId)s_%(productName)s_%(sd)s_%(ed)s.json' % {
            'productType': tname, 'productId': data.get('pid'), 'productName': data.get('pname'), 'sd': sd, 'ed': ed
        }
        # 构造请求参数
        url = "https://e.qq.com/ec/api.php"
        params = {"g_tk": self.g_tk, 'owner': self.uid, "product_id": data.get('pid'), "product_type": tid, "sdate": sd,
                  "edate": ed}
        headers = {
            "cookie": self.cookie_str,
            "referer": "http://e.qq.com/atlas/%(uid)s/report/analytic2?product_id=%(pid)s&product_type=%(ptype)s" % {
                'uid': self.uid, 'pid': data.get('pid'), 'ptype': tid
            }
        }
        self.params.update(params)
        self._headers.update(headers)
        data = get(url, params=self.params, headers=self._headers)
        if not data['is_success']:
            return {'succ': False, 'msg': data['msg']}

        file_name = os.path.join(self.dir_path, fname)
        data = data['msg'].json()
        cost = data.get('data').get('total').get('cost').replace(',', '')
        if float(cost) == 0:
            return {'succ': False, 'msg': 'no data'}
        data['account'] = self.acc
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        logger.info('crawled data: %s' % data)
        return {'succ': True}

    def get_data(self, sd, ed, data, tid, tname):
        logger.info('get into (self.get_data_common_version)function')
        url = "https://e.qq.com/ec/api.php"
        fname = '%(productType)s_%(productId)s_%(productName)s_%(sd)s_%(ed)s.json' % {
            'productType': tname, 'productId': data.get('pid'), 'productName': data.get('pname'),
            'sd': sd, 'ed': ed
        }
        # make params
        pdata = {
            "sdate": sd, "edate": ed, "product_type": tid, 'g_tk': self.g_tk, "product_id": data.get("pid"),
            "owner": self.uid
        }
        headers = {
            "cookie": self.cookie_str,
            "referer": "http://e.qq.com/atlas/%(uid)s/report/order_old?pid=%(pid)s&ptype=%(ptype)s" % {
                'uid': self.uid, 'pid': data.get('pid'), 'ptype': tid
            }
        }
        self.params['gtk'] = self.g_tk
        self.pdata.update(pdata)
        self._headers.update(headers)
        data = post(url, data=self.pdata, params=self.params, headers=self._headers)
        if not data['is_success']:
            return {'succ': False, 'msg': data.get('msg')}
        file_name = join(self.dir_path, fname)
        data = data['msg'].json()
        cost = data.get('data').get('total').get('cost').replace(',', '')
        if float(cost) == 0:
            return {'succ': False, 'msg': 'no data'}
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        logger.info('crawled data: %s' % data)
        return {'succ': True}

    def get_pids(self, tid, sd, ed):
        url = 'https://e.qq.com/ec/api.php'
        headers = {
            'accept': "application/json, text/javascript, */*; q=0.01",
            'cookie': self.cookie_str,
            'referer': "https://e.qq.com/atlas/%s/report/producttype" % self.uid,
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3569.0 Safari/537.36",
        }
        payload = {"mod": "report", "act": "getproduct", "g_tk": self.g_tk, "owner": self.uid, "sdate": sd,
                   "edate": ed, "searchtype": "product", "product_type": tid}
        data = post(url, data=payload, headers=headers, verify=False)
        if not data.get('is_success'):
            return {'succ': False, 'msg': data.get('msg')}
        data = data.get('msg').json()
        if not data.get('data') or not data.get('data').get('list'):
            return {'succ': False, 'msg': 'no data'}
        pdatas = [{'pname': e.get('pname'), 'pid': e.get('product_id')} for e in data.get('data').get('list')]
        return {'succ': True, 'msg': pdatas}

    def change_date(self, sd, ed):
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
        window.location.reload();
    }
})('%s', '%s');"""
        # 获取img
        dst_url = 'https://e.qq.com/atlas/%s/report/producttype' % self.uid
        self.d.get(dst_url)

        # 判断界面版本
        global page_version
        if u.wait_element(self.d, (By.ID, 'toolbar'), 10):
            page_version = 'new'
        self.d.execute_script(set_start_time % (sd, ed))  # 更新日期
        time.sleep(1)

    def get_data_process(self, dates):
        data_list, has_no_data_in_two_mth = [], []
        for sd, ed in dates:
            d_list = []
            tids = self.get_type_ids()  # 获取产品类型id
            if not tids.get('succ'):
                return tids
            for tid, tname in tids.get('msg'):
                pdatas = self.get_pids(tid, sd, ed)  # 获取产品类型信息
                if not pdatas.get('succ') and pdatas.get('msg') == 'no data':
                    d_list.append({'type_id': tid, 'pdata': None, 'tname': tname, 'has_data': False})
                    continue
                elif not pdatas.get('succ'):
                    return pdatas
                for p in pdatas.get('msg'):
                    if page_version:
                        data = self.get_data(sd, ed, p, tid, tname)  # 获取产品详细数据
                    else:
                        data = self.get_data_another_version(sd, ed, p, tid, tname)
                    if not data.get('succ') and data.get('msg') == 'no data':
                        d_list.append({'type_id': tid, 'pdata': p, 'tname': tname, 'has_data': False})
                        continue
                    if not data.get('succ'):
                        logger.warning({'type_id': tid, 'pdata': p, 'tname': tname, 'get_data': 'failed'})
                    d_list.append({'type_id': tid, 'pdata': p, 'tname': tname, 'has_data': True})
                    has_no_data_in_two_mth.append(1)
            data_list.extend([{'date': (sd, ed), 'data': d_list}])
        if not has_no_data_in_two_mth:
            self.result_kwargs['has_data'] = 0
        return {'succ': True, 'msg': data_list}

    def parse_balance(self):
        # parse
        res = self.login_obj.get_balance(self.uid)
        if not res.get('succ'):
            return res
        unknown_account_name_type = {}
        balance_data = {'现金账户': 0, '虚拟账户': 0, '信用账户': 0, '临时信用账户': 0}
        accounts = res.get('msg')
        keys = balance_data.keys()
        for i in accounts:
            account_name = i.get('account_name')
            if account_name in keys:
                balance_data[account_name] = round(i.get('balance')/100, 2)
            else:
                # unknown_account_name_type[account_name] = round(i.get('balance')/100, 2)
                continue
        header = ['账号', '现金账户', '虚拟账户', '信用账户', '临时信用账户', '总计']
        summary = sum(balance_data.values())
        balance_data['总计'] = summary
        balance_data['账号'] = self.acc
        if unknown_account_name_type:
            header.extend(unknown_account_name_type.keys())
            balance_data.update(unknown_account_name_type)
        return header, summary

    def login_part(self, ui):
        # 登陆
        self.login_obj = LoginQQ(self.user_info, self.platform)
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
        self.wait = WebDriverWait(self.d, 10)
        data = login_res.get('data')
        self.cookie_str = self.login_obj.cookies.get('cookie_str')
        self.g_tk = self.login_obj.gtk
        self.uid = data.get('uid')

    def get_data_part(self, *args, **kwargs):
        # 获取时间
        ui = self.user_info
        self.dates = ui.get('dates')
        ys, ms, ye, me = self.dates if self.dates else (None, None, None, None)
        mths, dates = u.make_dates(ms=ms, ys=ys, me=me, ye=ye)
        # 获取数据
        data_list = self.get_data_process(dates)
        return data_list

    def get_img_part(self, get_data_res=None, **kwargs):
        # 截图
        for d in get_data_res.get('msg'):
            sd, ed = d.get('date')
            self.d.get('https://e.qq.com/atlas/%s/report/producttype' % self.uid)
            self.change_date(sd, ed)
            total_pic_name = 'total_%s_%s.png' % (sd, ed)  # pic1 , 总消耗页面截图
            logger.info('start to cut img')
            cut_res = cut_img(None, self.dir_path, total_pic_name)
            if not cut_res['succ']:
                logger.error(cut_res['msg'])

            for dt in d.get('data'):
                if dt.get('has_data'):
                    try:
                        self.get_img(dt, sd, ed)
                    except Exception as ei:
                        logger.warning('get img failed!!   pic_msg: %s~%s -- %s' % (sd, ed, dt))
                        logger.error(ei, exc_info=1)
        return {'succ': True}

