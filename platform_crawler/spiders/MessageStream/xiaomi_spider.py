from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
import os
import json

from platform_crawler.utils.utils import Util
from platform_crawler.utils.post_get import get
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.spiders.pylib.task_process import TaskProcess, EC
from platform_crawler.spiders.get_login_data.login_xiaomi import XiaoMI
from platform_crawler.settings import join, JS_PATH


u = Util()

logger = None
base_header = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Cookie': None,
    'Host': "e.mi.com",
    'Referer': None,
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
}


is_child_account = False


class XiaoMiSpider(TaskProcess):

    def __init__(self, user_info, **kwargs):
        global logger
        self.child_account_filter = ['14222', 14222]            # 要过滤的子账号
        self.cookies = None
        self.service_token = None
        self.dates = None
        self.agent = None
        self.is_get_balance = False
        self.none_cost = None
        super().__init__(headers=base_header, user_info=user_info, **kwargs)
        logger = self.logger

    def get_child_accounts(self):
        """获取子账号列表"""
        url = 'http://e.mi.com/v2/account/agent/customers'
        headers = {'Cookie': self.cookies, 'Referer': "http://e.mi.com/v2/dist/agent.html"}
        self._headers.update(headers)
        querystring = {"agent": self.agent}     # 替换为agent
        data = get(url, params=querystring, headers=self._headers)
        if not data['is_success']:
            return {'succ': False, 'msg': data['msg']}
        data = data['msg'].json()
        if not data.get('success'):
            return {'succ': False, 'msg': data.get('failMsg'), 'desc': 'is_child_account'}
        # if reget:
        #     return self.get_child_accounts(agent, reget=False)
        accounts = [x.get('customerId') for x in data.get('result').get('list') if x.get('status') == 2]
        data = [i for i in data.get('result').get('list') if i.get('customerId') in self.none_cost]
        self.balance_data = {'list': data}
        return {'succ': True, 'accounts': accounts}

    def get_data(self, sd, ed, child_account, pid=None, pname=None, total=False):
        """
        获取数据
        :return:
        """
        # 处理文件名
        if total:
            pid, pname = ('', '')
            fname = '%s_%s_%s.json' % (child_account, sd, ed)
        else:
            fname = '%(childAcc)s_%(pname)s_%(start_date)s_%(end_date)s.json' % {
                'childAcc': child_account, 'pname': pname.strip(), 'start_date': sd, 'end_date': ed
            }
        file_name = os.path.join(self.dir_path, fname)
        if not pid and not total:  # 没有数据, 没有产品
            return {'succ': False, 'msg': 'no data'}
        # 处理请求参数
        url = 'http://e.mi.com/v2/report/dashboard'
        querystring = {"customerId": child_account,"serviceToken": self.service_token, "xiaomiId": self.acc,
                       "sdate": sd, "edate": ed, "campaign": pid}
        # 发送请求
        data = get(url, params=querystring, headers=self._headers)
        if not data['is_success']:
            return {'succ': False, 'msg': data['msg']}
        # 获取数据总数
        data = data['msg'].content.decode('utf-8')
        t_count = json.loads(data).get('result').get('conf').get('totalnum')
        if t_count == 0:  # 无消耗结算
            return {'succ': False, 'msg': 'no data'}
        # 写入文件
        with open(file_name, 'w', encoding='utf-8') as f:
            try:
                f.write(data)
            except Exception as e:
                logger.error(e, exc_info=1)
        logger.info('crawled data: --------' + data)
        return {'succ': True}

    def get_pid(self, child_account, sd, ed):
        url = 'http://e.mi.com/v2/campaign/list'
        ptype, pids = None, []
        if self.platform == 'XIAOMISTORE':
            ptype = ['1']
        elif self.platform == 'XIAOMIXXL':
            ptype = ['2', '3']
        querystring = {"customerId": str(child_account), "serviceToken": self.service_token, "xiaomiId": self.acc,
                       "page": "1", "pagesize": "2000", 'sdate': sd, 'edate': ed, 'type': ''}
        referer = "http://e.mi.com/v2/dist/data.html"
        for pt in ptype:
            querystring['type'] = pt
            res = self.deal_result(self.execute('GET', url, params=querystring, referer=referer), json_str=True)
            if not res.get('succ'):
                raise Exception(res.get('msg'))
            res = res.get('msg').get('result')
            if res.get('conf').get('totalnum') != 0:
                pds = [{'id': x.get('id'), 'name': x.get('name')} for x in res.get('list')]
                pids.extend(pds)
        return {'succ': True, 'msg': pids} if len(pids) != 0 else {'succ': False, 'msg': 'no data'}

    def get_data_process(self):
        """循环每个子账号爬取数据"""
        # 获取时间
        global is_child_account
        ys, ms, ye, me = self.dates
        mths, dates = u.make_dates(ms=ms, ys=ys, ye=ye, me=me)
        img_data = []
        err_list = []
        self.none_cost = []
        for sd, ed in dates:
            cal = self.get_child_accounts()  # get child_account_list
            if not cal.get('succ') and cal.get('desc') == 'is_child_account':
                is_child_account = True
                cal['accounts'] = [self.agent]
            elif not cal['succ']:
                return cal
            logger.info('the length of child account:  %s' % len(cal['accounts']))
            # 获取产品列表   child_account_product_id
            for ca in cal['accounts']:
                if ca in self.child_account_filter:
                    continue
                pids = self.get_pid(ca, sd, ed)
                if not pids.get('succ') and pids.get('msg') == 'no data':     # 没有计划
                    img_data.append({'child_account': ca, 'hasData': False, 'img': False})
                    logger.warning('child_account: %s, has no plan' % ca)
                    continue
                elif not pids['succ']:
                    err_list.append({'child_account': ca, 'hasData': None, 'sd': sd, 'ed': ed, 'img': False})
                    logger.error({'child_account': ca, 'hasData': None, 'sd': sd, 'ed': ed, 'img': False, 'msg': pids['msg']})
                    continue
                # 获取数据
                self.get_img(sd, ed, ca=ca, total=True)
                self.get_data(sd, ed, ca, total=True)
                for pid in pids.get('msg'):
                    res = self.get_data(sd, ed, ca, pid=pid.get('id'), pname=pid.get('name'))
                    if res['succ']:
                        img_data.append({'child_account': ca, 'name': pid.get('name'), 'hasData': True, 'sd': sd, 'ed': ed, 'img': False})
                    elif not res['succ'] and res['msg'] == 'no data':           # 没有数据
                        res_dict = {'child_account': ca, 'name': pid.get('name'), 'hasData': False, 'img': False}
                        img_data.append(res_dict)
                        if res_dict in img_data:
                            self.none_cost.append(ca)
                        logger.warning({'child_account': ca, 'hasData': False, 'img': False})
                    else:
                        err_list.append({'child_account': ca, 'hasData': None, 'sd': sd, 'ed': ed, 'img': False})
                        logger.error(res['msg'])  # 请求失败(网络问题)
                    time.sleep(0.25)
        return img_data

    def update_date_use_js(self, sd, ed):
        with open(join(JS_PATH, 'mi_vue_set_date.js'), 'r', encoding='utf-8') as f:
            date_js = f.read()
        sd = '/'.join(sd.split('-'))
        ed = '/'.join(ed.split('-'))
        js_text = '%s("%s", "%s");' % (date_js, sd, ed)
        self.d.execute_script(js_text)
        self.d.implicitly_wait(10)
        time.sleep(1)

    def delete_mask(self):
        js_path = join(JS_PATH, 'mi_delete_mask.js')
        with open(js_path, 'r', encoding='utf-8') as f:
            js = f.read()
        self.d.execute_script(js)
    
    def get_img(self, sd, ed, pname=None, ca=None, total=None, retries=1):
        url = 'http://e.mi.com/v2/dist/index.html#!/index/%s' % ca
        self.d.get(url)
        self.d.implicitly_wait(20)
        self.delete_mask()
        time.sleep(2)
        self.d.find_element_by_link_text('数据分析').click()
        # 选择计划
        if not total:
            self.d.find_element_by_css_selector('.cond-box .dropdown:nth-child(1) .dropdown-title').click()
            self.d.find_element_by_link_text('全选广告计划').click()
            self.d.find_element_by_link_text(pname.strip()).click()
        # 更新日期
        time.sleep(3)
        try:
            self.update_date_use_js(sd, ed)
        except:
            if retries >= 3:
                return {'succ': False}
            retries += 1
            print('failed %s times' % retries)
            return self.get_img(sd, ed, pname=pname, ca=ca, total=total, retries=retries)
        hjs = 'return h = document.querySelector("#table-header .emi-table-main-body table tbody").offsetHeight'
        height = self.d.execute_script(hjs)         # 获取页面高度
        self.delete_mask()
        if total:
            pic_name = '总数据_%(childAcc)s_%(sd)s_%(ed)s_detail.png' % {'childAcc': ca, 'sd': sd, 'ed': ed}
            cut_res = cut_img(None, self.dir_path, pic_name)      # 截图保存
            if not cut_res['succ']:
                logger.error('get img %s failed-------msg: %s' % (pic_name, cut_res.get('msg')))
            logger.info('height: %s ---picname: %s' % (height, pic_name))
            return cut_res
        pic_name_detail = '%(childAcc)s_%(pname)s_%(sd)s_%(ed)s_detail.png' % {
            'childAcc': ca, 'pname': pname.strip(), 'sd': sd, 'ed': ed
        }
        pic_name_whole = '%(childAcc)s_%(pname)s_%(sd)s_%(ed)s_whole.png' % {
            'childAcc': ca, 'pname': pname.strip(), 'sd': sd, 'ed': ed
        }
        cut_res = cut_img(None, self.dir_path, pic_name_whole)      # 截图保存
        self.d.execute_script("document.documentElement.scrollTop = 600")
        cut_img(height, self.dir_path, pic_name_detail, [15, 32], [1875, 988], [1872, 965])         # old: 255
        if not cut_res['succ']:
            logger.error('get img %s failed-------msg: %s' % (pic_name_detail, cut_res.get('msg')))
        logger.info('height: %s ---picname: %s' % (height, pic_name_detail))
        return cut_res

    def get_agent(self):
        """获取用户二代id"""
        if self.platform == 'XIAOMISTORE':
            self.wait_element(By.LINK_TEXT, '管理中心').click()
            time.sleep(0.5)
        # 子账号数据
        try:
            agents = self.wait_element(By.CSS_SELECTOR, '#user .detail span', ec=EC.presence_of_all_elements_located, wait_time=3)
            if len(agents) > 1:
                agent = self.wait_element(By.CSS_SELECTOR, '#user li:nth-child(3)').text
            else:
                agent = agents[0].text
        except:
            agent = self.wait_element(By.CSS_SELECTOR, '#user li:nth-child(3)').text
        self.agent = agent.split(':')[1].strip()

    def login_part(self, ui):
        if self.platform == 'XIAOMIXXL':
            return
        self.login_obj = XiaoMI(ui, ui.get('platform'))
        return self.login_obj.run_login()

    def deal_login_result(self, login_res):
        if self.platform == 'XIAOMIXXL':
            return
        if not login_res.get('succ'):
            return login_res
        self.d = login_res.get('driver')
        self.wait = WebDriverWait(self.d, 20, 0.5)
        cookies = login_res.get('cookies')
        self.service_token = [x.get('value') for x in cookies if x.get('name') == 'serviceToken'][0]
        self.cookies = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in cookies])
        self.dates = self.user_info.get('dates') if self.user_info.get('dates') else (None, None, None, None)
        self.get_agent()

    def get_balance(self):
        res = self.get_child_accounts()
        if res.get('succ'):
            return res
        # 子账号余额
        url = 'http://e.mi.com/v2/account/balance'
        querystring = {"customerId": self.agent, "serviceToken": self.service_token, "xiaomiId": self.acc}
        ref = 'http://e.mi.com/v2/dist/index.html'
        res = self.deal_result(self.execute('GET', url, params=querystring, referer=ref), json_str=True)
        if not res.get('succ') or not res.get('msg').get('success'):
            raise Exception(res.get('msg'))
        data = res.get('msg').get('result')
        self.balance_data = {'cash': data.get('cash').get('balance'), 'totalBalance': data.get('totalBalance')}

    def parse_balance(self):
        accts = self.balance_data.get('list', [])
        if not accts:
            # 子账号
            data = [{'账号': self.acc, '公司名': '', '现金余额': self.balance_data.get('cash'), '虚拟金余额': 0,
                     '总计': self.balance_data.get('totalBalance')}]
        else:
            data = [{'账号': self.acc,
                     '公司名': acct.get('companyName'),
                     '现金余额': acct.get('balance').get('cash'),
                     '虚拟金余额': acct.get('balance').get('virtual'),
                     '总计': acct.get('totalBalance')}
                    for acct in accts]
        headers = ['账号', '公司名', '现金余额', '虚拟金余额', '总计']
        logger.info('balance data : \n%s' % data)
        self.is_get_balance = True
        return headers, data

    def get_data_part(self, *args, **kwargs):
        # 获取数据
        img_data = self.get_data_process()
        for i in self.none_cost.copy():
            if self.none_cost.count(i) != 2:
                self.none_cost.remove(i)
        self.none_cost = list(set(self.none_cost))
        files = [x for x in os.listdir(self.dir_path) if 'json' in x]
        if not files:
            self.result_kwargs['has_data'] = 0
        return img_data

    def get_img_part(self, get_data_res=None, **kwargs):
        # 截图部分
        err_list = []
        for i in get_data_res:
            if i.get('hasData'):
                try:
                    res = self.get_img(i.get('sd'), i.get('ed'), pname=i.get('name'), ca=i.get('child_account'))
                    if not res['succ']:
                        i['img'] = True
                        err_list.append(i)
                        logger.error(res['msg'])
                except Exception as e:
                    logger.error(e, exc_info=1)
                    err_list.append(i)
        else:
            logger.warning(err_list)
        return {'succ': True}

    def run(self, ui):
        # 初始化路径数据
        self.init_paths(ui)

        # 登陆 && 获取数据/图片
        try:
            res = self.login_and_get_data(ui)
            if res is not None and not res.get('succ'):         # 正常的报错场景
                self.save_screen_shot(self.err_img_name)
        except Exception as er:
            self.save_screen_shot(self.err_img_name)        # 未知报错场景
            logger.error(er, exc_info=1)
            res = {'succ': False, 'msg': 'got unKnown error'}

        try:
            if self.platform == 'XIAOMIXXL':
                self.d.quit()
        except:
            pass

        # 检测是否有图片
        pics = [x for x in os.listdir(self.dir_path) if 'png' in x]
        if len(pics) == 0:
            self.result_kwargs['has_pic'] = 0
        # 上传结果
        self.upload_file()

        # 返回结果
        if not res.get('succ'):
            return res

        if self.platform == 'XIAOMISTORE':
            ui['platform'] = 'XIAOMIXXL'
            self.platform = 'XIAOMIXXL'
            return self.run(ui)

        # 获取账户余额
        try:
            self.get_account_balance()
        except Exception as err_acc:
            logger.error(err_acc, exc_info=1)

        return {'succ': True}
