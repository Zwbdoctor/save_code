# -*- coding: utf-8 -*-
'''
https://e.yunos.com  需要抓取数据生成excel
'''
from platform_crawler.spiders.MessageStream import aliSpider
from configs.aliyun_config import page_dict, img_dicts
from platform_crawler.utils.post_get import post, get
from platform_crawler.spiders.pylib.get_pwd import get_pwd
from platform_crawler.utils.utils import Util
import time
import os
import json
# import xlsxwriter
import xlrd
import xlwt
from xlutils.copy import copy   #支持对已经存在的文件进行读写
import requests

ask_sql_url = 'http://erp.btomorrow.cn/adminjson/adminjson/ERP_GetCrawlerTaskStatus'   # useless
post_res_url = 'http://erp.btomorrow.cn/adminjson/ERP_ReportPythonCrawlerTask'
fscapture = r'D:\fscapture\FSCapture.exe'

u = Util()
log_path = os.path.abspath('./logs/AliosExcel')
if not os.path.exists(log_path):
    os.makedirs(log_path)
logger = u.record_log(log_path, __name__)

real_ip = '139.224.116.116'
serv_parm = {
    'ip': real_ip, 'user': 'root', 'pwd': 'hhmt@pwd@123', 'dst_path': ''
}


class AliyunExcelSpider:
    def __init__(self, user_info):
        self.dst_path = '/data/python/%s/' % user_info['platform']
        self.dir_path = None
        self.line_path = None
        self.user_info = user_info
        self.acc = user_info['account']
        self.pwd = user_info['password']
        self.page_dict = page_dict
        self.img_dicts = img_dicts
        self.d = None
        self.wait = None
        self.init__post_param()
        # super(AliyunExcelSpider, self).__init__(user_info)

    def init__post_param(self):
        self.headers = {
            'Accept': "text/html,application/xhtml+xml,application/json,text/javascript,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            'Content-Type': "application/x-www-form-urlencoded",
            'cookie': None,
            'origin': "https://e.yunos.com",
            'referer': None,
            'Cache-Control': "no-cache",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
        }

    def saveSheet(self, headings, datas, subaccount):
        # try:
        #     if not hasattr(self, 'workbook'):
        #         # 创建excel
        #         # xlspath = os.path.join(self.dir_path, '%s_%s.xlsx' % (self.acc, self.pwd))
        #         xlspath = '%s_%s.xlsx' % (self.acc, self.pwd)
        #         self.workbook = xlsxwriter.Workbook(xlspath)

        #     # 自定义样式，加粗
        #     bold = self.workbook.add_format({'bold': 1})
        #     sheetname = '%s_%s' % (subaccount[0], subaccount[1])
        #     worksheet = self.workbook.add_worksheet(sheetname)
        #     worksheet.write_row('A1', headings, bold)

        #     idx = 1
        #     for data in datas:
        #         for dtidx, dtitem in enumerate(data):
        #             worksheet.write(idx, dtidx, dtitem)
        #         idx = idx+1
        #     return True
        # except Exception as e:
        #     self.workbook.close()
        #     logger.error('saveSheet|error %s' % e)
        #     return False
        try:
            xlspath = os.path.join(os.path.dirname(__file__), '%s.xlsx' % self.acc)
            if os.path.exists(xlspath):
                rb = xlrd.open_workbook(xlspath)
                workbook =  copy(rb)
            else:
                workbook = xlwt.Workbook()

            sheetname = '%s_%s' % (subaccount[0], subaccount[1])
            table = workbook.add_sheet(sheetname)
            datas.insert(0, headings)
            for rowidx,row in enumerate(datas):
                for itemidx,item in enumerate(row):
                    table.write(rowidx, itemidx, item)
            workbook.save(xlspath)

            return True
        except Exception as e:
            logger.error('saveSheet|error %s' % e)
            return False

    def open_page(self, url, cookie):
        self.d.get(url)
        self.d.delete_all_cookies()
        for ckitem in cookie['msg']:
            self.d.add_cookie(ckitem)
        time.sleep(1)
        self.d.get(url)
        time.sleep(2)

    def init_browser(self):
        from selenium import webdriver
        # from selenium.webdriver.chrome.options import Options
        # op = Options()
        # op.add_argument('--headless')
        # op.add_argument('--disable-gpu')
        # op.add_argument('log-level=3')
        # self.d = webdriver.Chrome(chrome_options=op)
        self.d = webdriver.Chrome()
        self.d.delete_all_cookies()
        self.d.set_page_load_timeout(60)
        self.d.set_script_timeout(60)
        self.d.maximize_window()

    def get_data_by_account(self, cookie, account, memberInfo):
        try:
            mths = u.make_months(1, 2018, 3, 2019)
            url = 'https://e.yunos.com/?identity=%s#/finance/list' % account[0]
            headings = []
            alldatas = []
            flag = 1

            for mth in mths:
                logger.info('get_data_by_account|start account:%s, mth:%s' % (account, mth))
                if flag == 1:
                    self.open_page(url, cookie)
                    flag = 2
                self.d.get(url)

                # 修改日期
                jsCon = None
                jspath = os.path.join(os.path.dirname(__file__), '../utils/ali_excel_changemonth.js')
                with open(jspath, 'r', encoding='utf-8') as f:
                    jsCon = f.read()
                jsCon = jsCon % { 'year':mth[0], 'month':mth[1] }
                self.d.execute_script(jsCon)

                time.sleep(3)

                # heading添加一次
                if len(headings)==0:
                    ths = self.d.find_elements_by_css_selector('.ant-table-thead th span')
                    for th in ths:
                        headings.append(th.text)
                    logger.info('get_data_by_account|headings:%s' % headings)

                datas = []
                trs = self.d.find_elements_by_css_selector('.ant-table-tbody tr')
                for tr in trs:
                    tmp = []
                    tds = tr.find_elements_by_css_selector('td')
                    for td in tds:
                        tmp.append(td.text)
                    datas.append(tmp)
                logger.info('get_data_by_account|datas:%s' % datas)
                alldatas = alldatas + datas

                # reload一下
                self.d.refresh()

            # 保存子账号sheet
            ss = self.saveSheet(headings, alldatas, account)
            if not ss:
                logger.error('get_data_by_account|saveSheet error')
                return False
            logger.info('get_data_by_account|saveSheet成功:%s' % account[0])

            return True
        except Exception as e:
            self.d.quit()
            logger.error('get_data_by_account|error %s' % e)
            return False

    def get_member_info(self, ckstr):
        url = 'https://e.yunos.com/api/member/info'
        headers = {
            'cookie': ckstr,
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            logger.error('get_member_info|status code %s' % res.status_code)
            return False
        res = res.content.decode('utf-8')
        return res

    def get_child_accounts(self, cookie, reget=True, psize='20'):
        """获取子账号列表"""
        url = 'https://e.yunos.com/api/member/agency/ref/list?keyword=&page_size=%s&page=1' % psize
        headers = {'cookie': cookie, 'referer': 'https://e.yunos.com/'}
        self.headers.update(headers)
        data = get(url, headers=self.headers)
        if not data['is_success']:
            return {'succ': False, 'msg': data['msg']}
        data = json.loads(data['msg'].content.decode())
        if reget:
            total_count = data.get('total_count')
            return self.get_child_accounts(cookie, reget=False, psize=total_count)
        accounts = [(x['username'], x['company']) for x in data['data'] if x['status'] == 1 and x['privilege'] == 1 and x['ref_status'] == 1]
        return {'succ': True, 'msg': accounts}

    def get_data(self, cookie):
        cookies = {e['name']: e['value'] for e in cookie['msg']}
        ckstr = '; '.join(['%s=%s' % (k, v) for k, v in cookies.items()])

        acctres = self.get_child_accounts(ckstr)
        if not acctres.get('succ'):
            logger.error('get_data|get_child_accounts error')
            return False
        accounts = acctres.get('msg')
        logger.info('get_data|获得accounts:%s' % accounts)
        self.init_browser()
        for account in accounts:
            memberInfo = self.get_member_info(ckstr)
            if not memberInfo:
                logger.error('get_data|get_member_info error, %s' % memberInfo)
                return False
            self.get_data_by_account(cookie, account, memberInfo)

        # 一个文件只能close一次
        # if hasattr(self, 'workbook'):
        #     self.workbook.close()

    def run_task(self, ui):
        # 创建文件夹
        ui['password'] = get_pwd(ui['password'])
        cutime = time.strftime('%Y-%m-%d')
        dir_name = '%(taskId)s_%(cTime)s_%(account)s' % {'taskId': ui['id'], 'cTime': time.strftime('%Y-%m-%d_%H-%M-%S'), 'account': self.acc}
        self.dir_path = os.path.join(os.path.abspath('./save_data/%s' % ui['platform']), cutime, dir_name)
        os.makedirs(self.dir_path)
        # 登陆
        first_cookie = aliSpider.LoginAlios(__name__)
        first_cookie = first_cookie.run_login(ui)
        if not first_cookie['succ']:
            return {'succ': False, 'msg': first_cookie['msg']}

        # 获得子账号财务数据(17.1到18.9；按子账号分sheet，总账号分excel)
        self.get_data(first_cookie)

        return {'succ': True, 'data_path': '%s/%s' % (cutime, dir_name)}



