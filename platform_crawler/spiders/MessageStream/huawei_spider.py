from selenium.webdriver.support.wait import WebDriverWait
import time
import os
import json

from platform_crawler.utils.utils import Util
from platform_crawler.utils.post_get import post
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.spiders.get_login_data import login_huawei
from platform_crawler.settings import join, JS_PATH
from platform_crawler.spiders.pylib.task_process import TaskProcess

u = Util()
logger = None
base_headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Content-Type': "application/json",
    'cookie': None,
    'origin': "https://developer.huawei.com",
    'referer': None,
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
}


class HuaWeiSpider(TaskProcess):

    def __init__(self, user_info, **kwargs):
        global logger
        self.need_list = [{'ca': 600000313, 'cname': ['关键词搜索', '推荐区']}]  # [{'ca': int, 'cname': []}]
        super().__init__(headers=base_headers, user_info=user_info, **kwargs)
        logger = self.logger
        self.balance_data = []
        self.cookies_str = None
        self.comp_has_none_cost = None

    def get_child_accounts(self, count=20):
        """获取子账号列表"""
        url = 'https://developer.huawei.com/consumer/cn/service/apcs/app/gwService'
        headers = {'cookie': self.cookies_str,
                   'referer': 'https://developer.huawei.com/consumer/cn/service/apcs/app/memberCenter.html'}
        self._headers.update(headers)
        params = {"agentAccountId": 0, "corpName": "", "accountId": 0, "status": "ALL", "fromRecCount": 0,
                  "maxReqCount": count, "localCurrentDate": time.strftime('%Y-%m-%d')}
        pdata = {"apiName": "AppPromote.Agent.queryCustomerList", "params": json.dumps(params)}
        data = self.deal_result(self.execute('POST', url, data=json.dumps(pdata)), json_str=True)
        if not data['succ']:
            return data
        data = data.get('msg').get('datas')
        total_count = data.get('totalCount')
        accounts = [x.get('accountId') for x in data.get('accounts')]
        if total_count > count:
            return self.get_child_accounts(count=total_count)
        # if self.comp_has_none_cost:
        self.balance_data = [{'account': x.get('corpName'), 'balance': x.get('balance'), 'id': x.get('accountId')}
                             for x in data.get('accounts')]
        #                    if x.get('accountId') in self.comp_has_none_cost]
        return {'succ': True, 'accounts': accounts}

    def get_pid(self, child_account, special=None):
        """
        获取产品id
        :param child_account: 子账号
        :return: pid list
        """
        url = 'https://developer.huawei.com/consumer/cn/service/apcs/app/gwService'
        headers = {
            "referer": "https://developer.huawei.com/consumer/cn/service/apcs/app/memberCenter.html?customerAccountId=%s" % child_account}
        self._headers.update(headers)
        params = {"fromRecCount": 1, "maxReqCount": 99999, "status": "AUDITED,RUN,SUSPENDED,DONE,CANCELED,TERMINATE",
                  "sortType": 0, "accountRegionType": "CHINA", "customerAccountId": child_account}
        pdata = {"apiName": "Inapp.Developer.queryTaskList", "params": json.dumps(params)}
        data = post(url, data=json.dumps(pdata), headers=self._headers)
        if not data['is_success']:
            raise Exception(data.get('msg'))
        data = json.loads(data['msg'].content.decode())
        # 对同名产品的不同id进行分组
        task_list = data.get('datas').get('taskList')
        pids = [(x.get('taskID'), x.get('contentAppName'), x.get('taskName')) for x in task_list] if data.get(
            'datas').get('totalCount') > 0 else []
        if special:
            pids = [x for x in pids if x[2] in special.get('cname')]
        after_distinct = list(set([e[1] for e in pids]))
        pgids = []
        for e in after_distinct:  # 合并重复项
            z = {'pname': e, 'pid': []}
            z.get('pid').extend([x[0] for x in pids if x[1] == e])
            pgids.append(z)
        logger.info(pgids)
        return {'succ': True, 'msg': pgids}

    def get_data(self, sd, ed, pid, pname, child_account):
        """
        获取数据
        """
        # 处理文件名
        sd = '%s%s%s' % tuple(sd.split('-'))
        ed = '%s%s%s' % tuple(ed.split('-'))
        fname = '%(childAcc)s_%(pname)s_%(sd)s_%(ed)s.json' % {
            'childAcc': child_account, 'pname': pname.strip(), 'sd': sd, 'ed': ed
        }
        file_name = os.path.join(self.dir_path, fname)
        if not pid:  # 没有数据, 没有产品
            with open(file_name, 'w') as f:
                f.write('{"msg": "no data"}')
            return {'succ': False, 'msg': 'no data'}
        # 处理请求参数
        url = "https://developer.huawei.com/consumer/cn/service/apcs/app/gwService"
        params = {"taskIDList": json.dumps(pid), "groupID": "ALL", "beginDate": sd, "endDate": ed,
                  "sortField": "task,time", "sortType": "0",
                  "maxRecCount": 999998, "fromRecCount": 1, "regions": "CN", "customerAccountId": child_account}
        pdata = {"apiName": "Inapp.Developer.reportPromoApp", "params": json.dumps(params)}

        # 发送请求
        data = self.deal_result(self.execute('POST', url, data=json.dumps(pdata)), json_str=True)
        if not data['succ']:
            raise Exception('Net error %s' % data.get('msg'))
        # 获取数据总数
        data = data.get('msg')
        t_count = data.get('datas').get('totalCount')
        if t_count == 0:  # 无消耗结算
            return {'succ': False, 'msg': 'no data'}
        # 写入文件
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        logger.info('crawled data: --------%s' % data)
        return {'succ': True}

    def get_data_process(self, dates=None):
        # 获取时间
        # mths, dates = u.make_dates(ms=12, ys=2018, ye=2018, me=12)
        ys, ms, ye, me = dates if dates else (None, None, None, None)
        mths, dates = u.make_dates(ms=ms, ys=ys, ye=ye, me=me)
        img_data = []
        for sd, ed in dates:
            logger.info('time-range ------ %s~%s' % (sd, ed))
            cal = self.get_child_accounts()  # get child_account_list
            if not cal['succ']:
                return cal
            logger.info('the length of child account:  %s' % len(cal['accounts']))
            for ca in cal['accounts']:  # 获取产品列表   child_account_product_id
                spe = None
                # if ca not in ['600000313', 600000313]:        # 单独爬取某个子账号
                #     continue
                for x in self.need_list:  # 针对特殊的子账户id，特殊的产品来获取产品id
                    if ca == x.get('ca'):
                        spe = x.get('cname')
                        pids = self.get_pid(ca, special=x)
                        break
                else:
                    pids = self.get_pid(ca)

                msg = {'child_account': ca, 'pname': None, 'sd': sd, 'ed': ed}
                for pid in pids.get('msg'):
                    res = self.get_data(sd, ed, pid.get('pid'), pid.get('pname'), ca)  # 获取数据
                    msg['pname'] = pid.get('pname')
                    if res['succ']:
                        msg.update({'hasData': True, 'img': False})
                    elif not res['succ'] and res['msg'] == 'no data':
                        msg.update({'hasData': False, 'img': False})
                        logger.warning(msg)
                    msg['special'] = spe if spe else ''
                    img_data.append(msg)
                    time.sleep(0.25)
        return img_data

    def update_date_click_version(self, sd, ed):
        # init select
        sd_list, ed_list = sd.split('-'), ed.split('-')
        sd_box = '.date-group > div:nth-child(1) .ucd-datepicker-input'
        ed_box = '.date-group > div:nth-child(2) .ucd-datepicker-input'
        drop_header_xpath = "//div[@class='ucd-datepicker ucd-datepicker-prevnext show']//div[@class='ucd-datepicker-dropdown-header']"
        year_list_xpath = "//div[@class='ucd-datepicker ucd-datepicker-prevnext show']//ul[@class='ucd-datepicker-list-y']/li"
        mth_list_xpath = "//div[@class='ucd-datepicker ucd-datepicker-prevnext show']//ul[@class='ucd-datepicker-list-m']/li"
        day_list = '//div[@class="ucd-datepicker ucd-datepicker-prevnext show"]//td[@class="ucd-datepicker-current"]'

        time.sleep(5)
        # select start date
        self.d.find_element_by_css_selector(sd_box).click()
        time.sleep(1)
        self.d.find_element_by_xpath(drop_header_xpath).click()
        time.sleep(1)
        for e in self.d.find_elements_by_xpath(year_list_xpath):  # start_year
            if sd_list[0] == e.text:
                e.click()
        time.sleep(1)
        for e in self.d.find_elements_by_xpath(mth_list_xpath):  # start_month
            if sd_list[1] == e.text:
                e.click()
        time.sleep(1)
        for e in self.d.find_elements_by_xpath(day_list):  # start_day
            if sd_list[2] == e.text:
                e.click()

        time.sleep(1)
        # select end date
        self.d.find_element_by_css_selector(ed_box).click()
        time.sleep(1)
        self.d.find_element_by_xpath(drop_header_xpath).click()
        time.sleep(1)
        for e in self.d.find_elements_by_xpath(year_list_xpath):  # end_year
            if ed_list[0] == e.text:
                e.click()
        time.sleep(1)
        for e in self.d.find_elements_by_xpath(mth_list_xpath):  # end_month
            if ed_list[1] == e.text:
                e.click()
        time.sleep(1)
        for e in self.d.find_elements_by_xpath(day_list):  # end_day
            if ed_list[2] == e.text:
                e.click()
        time.sleep(1)

        # 点击查询
        query_xpath = "//section[@class='apppromote-report section section-filled report-filter ng-isolate-scope " \
                      "ng-dirty ng-valid ng-valid-parse']//a[@class='btn btn-primary btn-small mr-2 ng-scope'][1]"
        self.d.find_element_by_xpath(query_xpath).click()

    def update_date_use_js(self, sd, ed):
        date_js = """
(function(st, et){
    var divStartTime = document.querySelector('div[ng-model="query.startTime"]')
    var scpStartTime = angular.element(divStartTime).scope();
    scpStartTime.query.startTime = st; 
    scpStartTime.$apply();
    divStartTime.querySelector('.ucd-datepicker-input').value = st;

    var divEndTime = document.querySelector('div[ng-model="query.endTime"]')
    var scpEndTime = angular.element(divEndTime).scope();
    scpEndTime.query.endTime = et;
    scpEndTime.$apply();
    divEndTime.querySelector('.ucd-datepicker-input').value = et;
})('%s', '%s'); 
        """
        self.d.execute_script(date_js % (sd, ed))
        with open(join(JS_PATH, 'huawei_delete_mask.js'), 'r', encoding='utf-8') as f:
            time_error = f.read()
        time.sleep(2)
        self.d.execute_script(time_error)
        # self.d.execute_script('document.querySelector("#ngdialog1").remove()')

    def get_img(self, ca, pname, sd, ed, special_account=None):
        url = 'https://developer.huawei.com/consumer/cn/service/apcs/app/memberCenter.html?customerAccountId=%s#/myReport/app-promote' % ca
        self.d.get(url)
        # 更新日期
        # self.update_date_use_js(sd, ed)
        # self.update_date_click_version(sd, ed)
        self.d.implicitly_wait(10)
        print(sd, ed)
        old_name = pname
        if special_account:
            print('=================================================\n')
            pname = '%s&%s' % (pname, special_account[0])  # 正常情况自动点击，非正常情况需要手动选日期
            input('please choose these selection then press enter to continue:\n%s' % special_account[0])
        last_mth_date_xpath = "/html/body/main/section/div/div/div/section/section[1]/div/div[4]/ul/li[1]"
        # this_month_xpath = '/html/body/main/section/div/div/div/section/section[1]/div/div[4]/ul/li[3]'
        if not special_account:
            self.d.find_element_by_xpath(last_mth_date_xpath).click()
            # self.d.find_element_by_xpath(this_month_xpath).click()
            # 点击查询
            query_xpath = "//section[@class='apppromote-report section section-filled report-filter ng-isolate-scope " \
                          "ng-dirty ng-valid ng-valid-parse']//a[@class='btn btn-primary btn-small mr-2 ng-scope'][1]"
            self.d.find_element_by_xpath(query_xpath).click()
        hjs = 'return h = document.body.offsetHeight'
        height = self.d.execute_script(hjs)
        pic_name = '%(childAcc)s_%(pname)s_%(sd)s_%(ed)s.png' % {
            'childAcc': ca, 'pname': pname.strip(), 'sd': sd, 'ed': ed
        }
        cut_res = cut_img(height, self.dir_path, pic_name)
        if not cut_res['succ']:
            logger.error('get img %s failed-------msg: %s' % (pic_name, cut_res.get('msg')))
        logger.info('height: %s ---picname: %s' % (height, pic_name))
        if special_account:
            special_account.remove(special_account[0])
            return self.get_img(ca, old_name, sd, ed, special_account=special_account)
        return cut_res

    def get_balance(self):
        # for x in self.comp_has_none_cost.copy():
        #     if self.comp_has_none_cost.count(x) != 2:       # 不是两个月都没数据的，就从余额数据中删除
        #         self.comp_has_none_cost.remove(x)
        # self.comp_has_none_cost = list(set(self.comp_has_none_cost))
        self.get_child_accounts()

    def parse_balance(self):
        header = ['账号', '余额']
        return header, self.balance_data

    def login_part(self, ui):
        self.login_obj = login_huawei.Huawei(ui, ui.get('platform'))
        return self.login_obj.run_login()

    def deal_login_result(self, login_res):
        if not login_res.get('succ'):
            return login_res
        self.d = login_res.get('driver')
        self.wait = WebDriverWait(self.d, 20)
        cookies = login_res.get('cookies')
        self.cookies_str = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in cookies])

    def get_data_part(self, ui, **kwargs):
        # 获取数据
        dates = ui.get('dates') if ui.get('dates') else None
        img_data = self.get_data_process(dates=dates)
        self.comp_has_none_cost = [i.get('child_account') for i in img_data if not i.get('has_data')]
        data_list = [1 for x in img_data if x.get('hasData')]
        if len(data_list) == 0:
            self.result_kwargs['has_data'] = 0
        if not self.is_get_img:
            # close real chrome
            self.login_obj.close_chrome_debugger(delete_user_data=True)
        self.get_account_balance()
        return img_data

    def get_img_part(self, get_data_res=None, **kwargs):
        # 截图部分
        err_list = []
        for i in get_data_res:
            if i.get('hasData'):
                try:
                    res = self.get_img(i.get('child_account'), i.get('pname'), i.get('sd'), i.get('ed'),
                                       special_account=i.get('special'))
                    if not res['succ']:
                        i['img'] = True
                        err_list.append(i)
                        logger.error(res['msg'])
                except Exception as e:
                    logger.error(e, exc_info=1)
        else:
            logger.warning(err_list)
        # logger.info('crawled 2 months data use time : -----%d' % int(time.time() - start_time))
        pics = [x for x in os.listdir(self.dir_path) if 'png' in x or 'jpg' in x]
        if len(pics) == 0:
            self.result_kwargs['has_pic'] = 0

        # close real chrome
        self.login_obj.close_chrome_debugger(delete_user_data=True)
