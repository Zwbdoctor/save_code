from lib.post_get import post, get
from lib.utils import Util
from lib.login_qq import LoginQQ

# from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
import json
import time
import os

u = Util()
log_name = 'app_store'
log_path = os.path.join(os.path.dirname(__file__), 'data')
data_files = os.listdir(log_path)
del_files = ['app_store.csv', 'app_store.log']
for x in del_files:
    if x in data_files:
        os.remove(os.path.join(log_path, x))
logger = u.record_log(log_path, 'app_store')
file_path = os.path.join(log_path, 'app_store.csv')


class AppTreasureGDT:

    def __init__(self):
        self.dir_path = None
        self.d = None
        self.wait = None
        self.cookie_str = None
        self.cookie = None
        self.g_tk = None
        self.uid = None
        self.user_info = None
        self.init__post_param()

    def init__post_param(self):
        self.headers = {
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            'Content-Type': "application/json",
            'cookie': None,
            'origin': "https://e.qq.com",
            'referer': None,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
        }

    def wait_element(self, ele_type, element, ec=EC.presence_of_element_located, wait_time=20):
        ele = WebDriverWait(self.d, wait_time).until(ec((ele_type, element)))
        return ele

    def getGTK(self, skey):
        hashes = 5381
        for letter in skey:
            hashes += (hashes << 5) + ord(letter)
        return hashes & 0x7fffffff
    
    def parse(self, data):
        # android_header = [
        #     "日期", "曝光量", "点击量", "消耗", "现金消耗", "激活量", "激活成本", "注册成本", "CPM", "CPC", "激活注册率", "点击激活率", "CPRA",
        #     "CTR", "CVR", "注册量", "次日留存率"]
        dkey = ['ios应用'] if self.user_info.get('type') == 'IOS' else ['Android应用']
        d = lambda z: 0 if (z == '-') or (z == '') else z
        dat = []
        if not data.get('data').get('list'):
            return False
        if self.user_info.get('account_type') == '255穿搭':
            dkey = ['Android应用', '应用宝推广', '本页总计']
            summary = data.get('data').get('summary')
            def z(x):
                x = x.replace(',', '')
                if '%' in x:
                    x = x.replace('%', '')
                    x = float(x)/100
                x = float(x)
                return x
            summary = {k: z(v) for k, v in summary.items()}
            summary['product_type_name'] = '本页总计'
            data.get('data').get('list').append(summary)
        for x in data.get('data').get("list"):
            if x.get('product_type_name') in dkey:
                x = {k: d(v) for k, v in x.items()}
                day = int(time.strftime('%d'))-1
                day = '%s-%s' % (time.strftime('%Y-%m'), day)
                cost = x.get('cost')/100
                everage_download = (cost/x.get('download')) if x.get('download') != 0 else 0
                cash_cost = cost / 1.1
                act_cost = (cost / x.get('activated_count')) if x.get('activated_count') != 0 else 0
                dat.append([day, x.get('product_type_name'), self.user_info.get('account'), self.user_info.get('user_id'), self.user_info.get('account_type'),
                    x.get('view_count'), x.get('valid_click_count'), cost, cash_cost, x.get('download'), everage_download, x.get('activated_count'), act_cost])
        if not dat:
            logger.info('not crawled data --- account: %s' % self.user_info.get('account'))
            return True
        with open(file_path, 'a') as f:
            for d in dat:
                f.write(','.join([str(x) for x in d]) + '\n')
        return True

    def get_data(self):
        url = "https://e.qq.com/ec/api.php"
        # make params
        params = {"mod": "report", "act": "getproducttype", "g_tk": str(self.g_tk), "owner": str(self.uid), "unicode": "1", "post_format": "json"}
        day = int(time.strftime('%d'))-1
        day = '%s-%s' % (time.strftime('%Y-%m'), day)
        pdata = {"page":1, "pagesize": 20, "sdate": day, "edate": day, "dynamic_field_list": "", "time_rpt": 1}
        headers = {
            "cookie": self.cookie_str,
            "referer": "https://e.qq.com/atlas/%s/report/producttype" % self.uid
        }
        self.headers.update(headers)
        data = post(url, data=json.dumps(pdata), params=params, headers=self.headers)
        if not data['is_success']:
            return {'succ': False, 'msg': data.get('msg')}
        data = data['msg'].json()
        data = self.parse(data)
        logger.info('crawled data: %s' % data)
        return {'succ': True}

    def parse_plan(self, data, plan_name):
        dat = [['计划名称', '曝光量', '点击量', '点击率', '点击均价', '花费']]
        for d in data.get('data').get('list'):
            if plan_name in d.get('campaignname'):
                ctr = round(d.get('ctr')*10000)/100
                cpc = round(d.get('cpc'))/100
                dat.append([d.get('campaignname'), d.get('view_count'), d.get('valid_click_count'), '%s%%' % ctr, cpc, d.get('cost')/100])
        with open(file_path, 'a') as f:
            for d in dat:
                f.write(','.join([str(x) for x in d]) + '\n')
            f.write('\n')

    def get_plan_data(self, plan_name):
        url = "https://e.qq.com/ec/api.php"
        day = int(time.strftime('%d'))-1
        day = '%s-%s' % (time.strftime('%Y-%m'), day)
        params = {"mod": "report", "act": "campaign", "g_tk": str(self.g_tk), "owner": str(self.uid), "unicode": "1",
                  "page":1, "pagesize": 20, "sdate": day, "edate": day, 'reportonly': 0, 'status': 999, 'time_rpt': 0}
        headers = {
            "cookie": self.cookie_str,
            "referer": "https://e.qq.com/atlas/%s/report/campaign?page=1&pagesize=20&reportonly=0&status=999&searchname=&sdate=%s&edate=%s" % (
                self.uid, day, day)
        }
        self.headers.update(headers)
        data = get(url, params=params, headers=self.headers)
        if not data['is_success']:
            return {'succ': False, 'msg': data.get('msg')}
        data = data['msg'].json()
        self.parse_plan(data, plan_name)
        logger.info('crawled data: %s' % data)
        return {'succ': True}

    def run(self, ui):
        # 创建本地目录
        self.dir_path = os.path.join(os.path.dirname(__file__), 'data')
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)

        # 登陆
        lq = LoginQQ(ui, log_name)
        login_res = lq.run_login()
        if not login_res['succ']:
            return login_res
        if login_res.get('msg') == 'unknown situation':
            logger.warning('got unknown login situation: %s' % login_res.get('desc'))
            return {'succ': True, 'msg': 'pass'}

        # self.d = login_res.pop('driver')
        # self.wait = WebDriverWait(self.d, 10)
        # data = login_res.get('data')
        self.cookie = login_res.get('cookie')
        cookie = {e.get('name'): e.get('value') for e in self.cookie}
        skey = cookie.get('gdt_protect') if cookie.get('gdt_protect') else cookie.get('skey')
        self.g_tk = self.getGTK(skey)
        self.cookie_str = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in self.cookie])
        self.uid = ui.get('user_id')

        # 获取数据
        if ui.get('plan_name'):
            self.get_plan_data(ui.get('plan_name'))
        data_list = self.get_data()
        if not data_list:
            return {'succ': False}
        return {'succ': True}

    def run_task(self, um):
        self.user_info = um
        try:
            res = self.run(um)
            # 上报服务器
            if res['succ']:
                # 成功
                logger.info('Crawler done!')
            else:
                logger.error('Crawler got something error, maybe this will help you to resolve: \n%s' % res)
        except Exception as e:
            logger.error('Crawler got something error, maybe this will help you to resolve:')
            logger.error(e, exc_info=1)
            self.d.quit()


def run():
    header = [
        "日期", "分类", "账号", "账户ID", "账户类别", "曝光量", "点击量", "消耗", "现金消耗", "下载量", "下载均价", "激活量", "激活成本", "注册成本", "CPM", "CPC", "点击下载率", 
        "下载激活率", "激活注册率", "点击激活率", "CPRA", "CTR", "CVR", "注册量", "次日留存率"]
    with open(file_path, 'w') as f:
        f.write(','.join(header) + '\n')
    user_list = [
        # {'account': '177443597', 'password': 'xhs112358', 'type': '安卓', 'account_type': '607穿搭搜索', 'user_id': '8649607', 'plan_name': '搜索广告-留存率'},
        # {'account': '3432413493', 'password': 'xhs112358', 'type': 'IOS', 'account_type': '710穿搭', 'user_id': '8506710'},
        # {'account': '2889320699', 'password': 'xhs11235813', 'type': 'IOS', 'account_type': '598彩妆', 'user_id': '8649598'},
        # {'account': '3308701393', 'password': 'xhs112358', 'type': '安卓', 'account_type': '519穿搭', 'user_id': '8180519'},
        # {'account': '2396684680', 'password': 'xhs112358', 'type': '安卓', 'account_type': '785发型', 'user_id': '8513785'},
        # {'account': '177443597', 'password': 'xhs112358', 'type': '安卓', 'account_type': '607穿搭', 'user_id': '8649607'},
        {'account': '1689735763', 'password': 'xhs112358', 'type': '安卓', 'account_type': '305测试', 'user_id': '9314305'},
        {'account': '3622467701', 'password': 'xhs112358112358', 'type': '安卓', 'account_type': '255穿搭', 'user_id': '8656255'},
        # {'account': '1842388297', 'password': 'xhs112358', 'type': '安卓', 'account_type': '535美甲', 'user_id': '9429535'},
        # {'account': '1708472653', 'password': 'xhs112358', 'type': '安卓', 'account_type': '262美食', 'user_id': '9425262'},
        {'account': '2700808615', 'password': 'xhs112358', 'type': 'IOS', 'account_type': '243发型', 'user_id': '9425243'},
    ]
    for ui in user_list:
        qq = AppTreasureGDT()
        qq.run_task(ui)
        del(qq)
        time.sleep(1)


if __name__ == "__main__":
    run()