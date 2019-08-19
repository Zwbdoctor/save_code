"""
vivo应用商店 zwb
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
import os
import json

from platform_crawler.utils.utils import Util
from platform_crawler.utils.post_get import post
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.spiders.pylib.task_process import TaskProcess
from platform_crawler.spiders.get_login_data.login_vivo import Vivo

u = Util()
logger = None

base_header = {
    'Accept': "application/json, text/javascript, */*; q=0.01",
    'Content-Type': "application/x-www-form-urlencoded",
    'Cookie': None,
    'Host': "cpd.vivo.com.cn",
    'Origin': "https://cpd.vivo.com.cn",
    'Referer': "https://cpd.vivo.com.cn/bplantdata/pageDataReport.action",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
}


class VivoSpider(TaskProcess):

    def __init__(self, user_info, **kwargs):
        global logger
        self.dates = None
        self.cookies = None
        super().__init__(headers=base_header, user_info=user_info, **kwargs)
        logger = self.logger
        self.flag = None
        self.none_cost_list = None

    def get_data(self, sd, ed, cookie, pnum=1, content=None, child_acc=None):
        """
        获取数据
        """
        url = 'https://cpd.vivo.com.cn/bplantdata/ajaxPageDataReport.action'
        # 处理文件名
        child_acc_name = child_acc if child_acc else self.acc
        fname = '%s_%s_%s.json' % (child_acc_name, sd, ed)
        file_name = os.path.join(self.dir_path, fname)
        payload = {
            "dataReportRequest.queryStartDate": sd,
            "dataReportRequest.queryEndDate": ed, "page.currentPageNum": pnum
        }
        self._headers.update({'Cookie': cookie})
        # 处理数据
        data = post(url, data=payload, headers=self._headers)
        if not data.get('is_success'):
            raise Exception(data.get('msg'))
        data = data.get('msg').content.decode('utf-8')
        data = json.loads(data)
        if data.get('page').get('recordCount') == 0:
            logger.warning(f'no data | child_acc:{child_acc} | range: {sd} ~ {ed}')
            return {'succ': False, 'msg': 'no data'}
        content = content if isinstance(content, list) else []
        page_num = data.get('page').get('currentPageNum')
        page_count = data.get('page').get('pageCount')
        content.extend(data.get('dataReportResponseList'))
        if page_num != page_count:
            pnum += 1
            return self.get_data(sd, ed, cookie, pnum=pnum, content=content, child_acc=child_acc)
        # 写入文件
        with open(file_name, 'w', encoding='utf-8') as f:
            try:
                json.dump({'data': content}, f)
            except Exception as e:
                logger.error(e, exc_info=1)
        logger.info('crawled data: -------- %s' % data)
        return {'succ': True}

    def get_balance(self):
        """获取非子账号的余额"""
        # 二代账号
        if self.flag:
            self.get_cid(get_bal=True)
            if not self.balance_data:   # 二代账号，没有子账号
                return {'succ': True}
            for x in self.balance_data:
                x.pop('name')
            logger.info('balance_data: %s' % self.balance_data)
            return {'succ': True}
        # 普通账号
        if len(self.none_cost_list) < 2:
            return {'succ': True}
        url = 'https://cpd.vivo.com.cn/account/queryBalance.action'
        ref = 'https://cpd.vivo.com.cn/planIdea/overview.action'
        res = self.deal_result(self.execute('GET', url, referer=ref), json_str=True)
        if not res.get('succ'):
            raise Exception(res.get('msg'))
        balance = float(res.get('msg').get('balance'))
        self.balance_data = [{'账户余额': balance}]
        logger.info('balance_data: %s' % self.balance_data)
        return {'succ': True}

    def get_cid(self, get_bal=False):
        """二代账号获取子账号"""
        url = "https://id.vivo.com.cn/api/account/querySubAccountList"
        headers = {
            'Accept': "application/json, text/javascript, */*; q=0.01",
            'Content-Type': "application/x-www-form-urlencoded",
            'Cookie': self.cookies,
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
        }
        payload = {'param': '{"page": 1,"size": 20,"pageIndex": 1,"pageSize": 20}'}
        data = post(url, data=payload, headers=headers)
        if not data.get('is_success'):
            raise Exception(data.get('msg'))
        data = data.get('msg').content.decode('utf-8')
        data_list = json.loads(data).get('object').get('list')
        if not data_list:
            logger.info('none child account')
            return {'succ': True, 'msg': []}
        # 获取没有消耗的子账号的余额
        if get_bal:
            self.balance_data = [{'账号': i.get('companyName'), '现金余额': i.get('cpdCashBalance'),
                                  '虚拟金余额': i.get('cpdDiscountBalance'), 'name': i.get('name')}
                                 for i in data_list
                                 if i.get('status') == 2 and i.get('name') in self.none_cost_list]
            return
        uids = [(e.get('name'), e.get('uuid')) for e in data_list if e.get('status') == 2]
        return {'succ': True, 'msg': uids}

    def get_child_cookie(self, cid):
        """获取子账号cookie"""
        url = 'https://cpd.vivo.com.cn/planIdea/overview.action?uuid=%s' % cid
        self.d.get(url)
        ck = self.d.get_cookies()
        ck = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in ck])
        return ck

    def the_same_get_data_proc(self, res, sd, ed, cname=None):
        """根据数据结果，判断是否截图"""
        if not self.is_get_img:
            logger.info('skip get img part')
            return
        if res.get('succ'):
            img_res = self.get_img(sd, ed, cname)  # 截图
            if not img_res.get('succ'):
                logger.error(img_res)
        elif not res.get('succ') and res.get('msg') == 'no data':
            if cname:
                logger.warning('child_account: %s, --- has no data' % cname)
            else:
                logger.warning({'acc': self.acc, 'hasData': False, 'img': False})
        else:
            logger.error(res)

    def get_data_process(self):
        """获取所有数据(数据，图片)"""
        # 获取时间
        ys, ms, ye, me = self.dates if self.dates else (None, None, None, None)
        mths, dates = u.make_dates(ms=ms, ys=ys, ye=ye, me=me)
        try:
            self.d.implicitly_wait(3)
            self.d.find_element_by_class_name('content-title')  # 二代账号
            self.flag = True
            logger.info('二代账号')
        except:
            self.flag = False
            logger.info('普通账号')
        none_cost_in_two_mth = []
        for sd, ed in dates:
            if self.flag:
                # 二代账号
                cids = self.get_cid()
                if not cids.get('msg'):
                    continue
                for cname, cuid in cids.get('msg'):
                    child_cookie = self.get_child_cookie(cuid)
                    res = self.get_data(sd, ed, child_cookie, child_acc=cname)
                    if not res.get('succ') and res.get('msg') == 'no data':
                        none_cost_in_two_mth.append(cname)
                        continue
                    self.the_same_get_data_proc(res, sd, ed, cname=cname)
                    time.sleep(0.25)
            else:
                # 普通账号
                res = self.get_data(sd, ed, self.cookies)  # 处理数据
                if not res.get('succ') and res.get('msg') == 'no data':
                    none_cost_in_two_mth.append(self.acc)
                    continue
                self.the_same_get_data_proc(res, sd, ed)
                time.sleep(0.25)
        # 移除有消耗的
        for x in none_cost_in_two_mth.copy():
            if none_cost_in_two_mth.count(x) == 1:
                none_cost_in_two_mth.remove(x)
        self.none_cost_list = set(none_cost_in_two_mth)

    def update_date_use_js(self, sd, ed):
        date_js = """
document.querySelector('#startDate').value="%s";
document.querySelector('#endDate').value="%s";
"""
        self.d.execute_script(date_js % (sd, ed))
        self.wait_element(By.CSS_SELECTOR, '.seaide_btn').click()  # 点击查询

    def get_img(self, sd, ed, cname):
        """截图操作"""
        # 转到目标页
        url = 'https://cpd.vivo.com.cn/bplantdata/pageDataReport.action'
        self.d.get(url)
        # 更新日期
        self.wait_element(By.ID, 'startDate')
        self.update_date_use_js(sd, ed)

        # 截图
        if not cname:
            cname = self.acc
        pic_name = '%s_%s_%s.png' % (cname, sd, ed)
        cut_res = cut_img(None, self.dir_path, pic_name)
        if not cut_res['succ']:
            logger.error('get img %s failed-------msg: %s' % (pic_name, cut_res.get('msg')))
        logger.info('got a picture ---picname: %s' % pic_name)
        return cut_res

    def parse_balance(self, *args, **kwargs):
        header = ['账号', '现金余额', '虚拟金余额', '账户余额', '总计']
        return header, self.balance_data

    def login_part(self, ui, **kwargs):
        self.login_obj = Vivo(ui, ui.get('platform'))
        return self.login_obj.run_login()

    def deal_login_result(self, login_res):
        if not login_res.get('succ'):
            return login_res
        self.d = login_res.get('driver')
        self.wait = WebDriverWait(self.d, 20)
        cookies = login_res.get('cookies')
        self.cookies = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in cookies])

    def get_data_and_imgs(self, ui, **kwargs):
        # 获取数据
        self.get_data_process()
        self.get_account_balance()

        files = [x for x in os.listdir(self.dir_path) if 'json' in x]
        if not files:
            self.result_kwargs['has_data'] = 0
        return {'succ': True}

