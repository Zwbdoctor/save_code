from platform_crawler.utils.utils import Util
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.spiders.pylib.login_qq import LoginQQ
from platform_crawler.spiders.pylib.task_process import TaskProcess


from selenium.webdriver.common.by import By
import json
import time
import os


u = Util()

page_version = 'old'
logger = None
base_header = {
    "accpet": "application/json, text/javascript, */*; q=0.01",
    "cookie": None,
    "origin": "https://e.qq.com",
    "referer": None,
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
}


class AppTreasure(TaskProcess):

    def __init__(self, user_info, **kwargs):
        global logger
        self.dates = None
        self.init__post_param()
        self.uid = None
        self.gtk = None
        self.cookie_str = None
        self.new_version = False
        super().__init__(headers=base_header, user_info=user_info, **kwargs)
        logger = self.logger

    def init__post_param(self):
        self.params = {
            "mod": "report", "act": "kacpaproduct", "g_tk": None,
        }

    def get_into_data_page(self):
        """跳转至截图页面"""
        time.sleep(1)
        self.wait_element(By.CSS_SELECTOR, '#navtabs .active a', wait_time=3).click()
        self.new_version = True
        return

    def get_img(self):
        """截图，并处理图片文件"""
        set_start_time = """
(function(st, et){
    if(jQuery('#daterange') && 
        jQuery('#daterange').data('daterangepicker') && 
        ('setStartDate' in jQuery('#daterange').data('daterangepicker'))
    ) {
        jQuery('#daterange').data('daterangepicker').setStartDate(st);
        jQuery('#daterange').data('daterangepicker').setEndDate(et);
        document.querySelector('.applyBtn').click();
    }
})('%s', '%s');"""
        set_start_time2 = """
(function(st, et){
    let settime = Date.now();
    localStorage.setItem('list_sdate', '{"data":"'+st+'","_time":'+settime+',"_expire":31308148}');
    localStorage.setItem('list_edate', '{"data":"'+et+'","_time":'+settime+',"_expire":31308148}');
}
)('%s', '%s');"""
        # try:
        ys, ms, ye, me = self.dates if self.dates else (None, None, None, None)
        mths, dates = u.make_dates(ys=ys, ms=ms, ye=ye, me=me)
        for sd, ed in dates:
            try:
                self.d.execute_script(set_start_time2 % (sd, ed))
                self.d.refresh()
            except:
                self.d.execute_script(set_start_time % (sd, ed))    # 更新日期

            if self.new_version:
                self.wait_element(By.LINK_TEXT, '应用宝推广', wait_time=5).click()
            '''
        # 等待数据表
        if not u.wait_element(self.d, (By.CLASS_NAME, 'spaui-table-tbody-wraper'), 5):
        if not u.wait_element(self.d, (By.ID, '_list'), 5):
        if get_times > 4:
        return {'succ': False, 'msg': 'not get table element after refresh 3 times'}
        get_times += 1
        return self.get_img(get_times=get_times, new_version=new_version)
        else:
        page_version = 'new'
        '''
            # 截图
            pic_name = '%s_%s.png' % (sd, ed)
            cut_res = cut_img(None, self.dir_path, pic_name)
            if not cut_res['succ']:
                logger.error('cut picture failed, possible msg:\ndir_path:%s\npic_name: %s' % (self.dir_path, pic_name))
            logger.info('got a picture: pic_msg: %s' % os.path.join(self.dir_path, pic_name))
            time.sleep(2)
        else:
            return {'succ': True}
        # except Exception as e:
        #     logger.error(e, exc_info=1)
        #     return {'succ': False, 'msg': traceback.format_exc()}

    def has_cost(self, sd, ed, ptype='35'):
        url = "https://e.qq.com/ec/api.php"
        params = {'act': 'getproduct', "g_tk": self.gtk, 'sdate': sd, 'edate': ed, 'searchtype': 'product',
                  'product_type': ptype}
        headers = {
            "cookie": self.cookie_str,
            "referer": "https://e.qq.com/atlas/%s/report/producttype" % self.uid,
        }
        self.params.update(params)
        self._headers.update(headers)
        data = self.deal_result(self.execute('GET', url, params=self.params), json_str=True)
        if not data.get('succ'):
            raise Exception(data.get('msg'))
        data = data.get('msg')
        total = data.get('data').get('total')
        if not total:
            return {'succ': False, 'msg': 'no data'}
        cost = float(total.get('cost', '0').replace(',', ''))
        if cost == 0:
            return {'succ': False, 'msg': 'no data'}
        pname = data.get('data').get('list')[0].get('pname')
        pid = data.get('data').get('list')[0].get('product_id')
        return {'succ': True, 'pname': pname, 'pid': pid}

    def get_data_v2(self, sd, ed, ptype='35', pname=None, pid=None):
        logger.info('get data :  version 2')
        url = "https://e.qq.com/ec/api.php"
        params = {"act": 'producttypedetail', "g_tk": self.gtk, 'owner': self.uid, 'product_type': ptype, "sdate": sd,
                  "edate": ed}
        headers = {
            "cookie": self.cookie_str,
            "referer": "https://e.qq.com/atlas/%s/report/analytic2?product_type=%s" % (self.uid, ptype)
        }
        self.params.update(params)
        self._headers.update(headers)
        data = self.deal_result(self.execute('GET', url, params=self.params), json_str=True)
        if not data['succ']:
            raise Exception(data.get('msg'))
        day_name = '%s_%s.json' % (sd, ed) if sd != ed else '%s.json' % sd
        file_name = os.path.join(self.dir_path, day_name)
        data = data.get('msg')
        data.update({'account': self.acc, 'pname': pname, 'pid': pid})
        with open(file_name, 'w') as f:
            json.dump(data, f)
        logger.info('crawled data: %s' % data)
        return {'succ': True}

    def parse_balance(self, *args, **kwargs):
        # parse
        # if self.result_kwargs.get('has_data') == 1:
        #     return {'succ': False}
        res = self.login_obj.get_balance(self.uid)
        if not res.get('succ'):
            return res
        unknown_account_name_type = {}
        balance_data = {'现金账户': 0, '虚拟账户': 0, '信用账户': 0}
        accounts = res.get('msg')
        keys = balance_data.keys()
        for i in accounts:
            account_name = i.get('account_name')
            if account_name in keys:
                balance_data[account_name] = round(i.get('balance')/100, 2)
            else:
                # unknown_account_name_type[account_name] = round(i.get('balance')/100, 2)
                continue
        header = ['账号', '现金账户', '虚拟账户', '信用账户', '总计']
        summary = sum(balance_data.values())
        balance_data['总计'] = summary
        balance_data['账号'] = self.acc
        if unknown_account_name_type:
            header.extend(unknown_account_name_type.keys())
            balance_data.update(unknown_account_name_type)
        return header, summary

    def login_part(self, ui, **kwargs):
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
        data = login_res.get('data')
        self.uid = data.get('uid')
        self.gtk = self.login_obj.gtk
        self.cookie_str = self.login_obj.cookies.get('cookie_str')

    def get_data_part(self, ui, **kwargs):
        # 获取时间
        self.dates = self.user_info.get('dates')
        ys, ms, ye, me = self.dates if self.dates else (None, None, None, None)
        mths, dates = u.make_dates(ms=ms, ys=ys, me=me, ye=ye)

        # 获取上个月到现在每天的数据
        data_list = []
        for sd, ed in dates:
            res = self.has_cost(sd, ed)
            if not res.get('succ'):
                continue
            self.get_data_v2(sd, ed, pname=res.get('pname'), pid=res.get('pid'))
            data_list.append(1)
        if not data_list:
            self.result_kwargs['has_data'] = 0

    def get_img_part(self, *args, **kwargs):
        # 截图操作
        time.sleep(2)
        self.get_into_data_page()
        self.get_img()
