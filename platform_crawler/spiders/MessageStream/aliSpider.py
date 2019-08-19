from random import choice
from ctypes import windll
import time
import json

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from requests.utils import quote

from platform_crawler.spiders.pylib.task_process import TaskProcess
from platform_crawler.spiders.get_login_data.BaseModel import Base
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.utils.post_get import post, get
from platform_crawler.utils.utils import Util
from platform_crawler.settings import IMG_PATH, join, BASEDIR


u = Util()
page_dict = {'url': 'http://e.yunos.com/', 'pst': 3,
             'ret_data': {'type': 9, 'account': "wangdi@btomorrow.cn", 'cookie': None},
             'host': ['e.yunos.com', '.yunos.com'], 'opera_type': 'sys',
             'delete_host_cookie': [
                 'g.alicdn.com', '.mmstat.com', 'e.yunos.com', '.yunos.com'
             ]}
base_header = {
    'Accept': "text/html,application/xhtml+xml,application/json,text/javascript,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'Content-Type': "application/x-www-form-urlencoded",
    'cookie': None,
    'origin': "https://e.yunos.com",
    'referer': None,
    'Cache-Control': "no-cache",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
}
logger = None


class LoginAlios(Base):

    def __init__(self, spider=None):
        self.acc, self.pwd = None, None
        if spider:
            global logger
            from logging import getLogger
            logger = getLogger(spider)
        super().__init__()

    def slide_vc_block(self, vc_location):
        # 滑动滑块
        with open(join(BASEDIR, 'utils', 'ali_slide_lines.json'), 'r') as f:
            lines = json.load(f)
        steps = choice(lines)
        u.pag.mouseDown(x=vc_location[0], y=vc_location[1])
        length, h = 0, 0
        for x, y, sleep in steps:
            length += x
            h += y
            windll.user32.SetCursorPos(int(vc_location[0]+length), int(vc_location[1]+h))
            time.sleep(sleep)
            if length > 229:
                break
        u.pag.mouseUp(x=vc_location[0]+229, y=vc_location[1])

    def click_function(self):
        imgs_path = join(IMG_PATH, 'aliyun_imgs')
        img_dicts = {
            'user_name': join(imgs_path, 'user_name.png'),
            'passwd': join(imgs_path, 'passwd.png'),
            'btn_login': join(imgs_path, 'btn_login.png'),
            'vc_block': join(imgs_path, 'verify_box.png')
        }
        un_lc = u.click_img_center(img_dicts['user_name'])
        if not un_lc:
            logger.warning('do not get user_name location')
            return {'succ': False, 'msg': 'do not get user_name location'}
        time.sleep(1)
        u.pag.typewrite(self.acc, interval=0.3)     # 输入用户名
        # self.key_input(st=self.acc, press_sleep=0.3)
        time.sleep(2)
        u.pag.click(140, 115)

        pd_lc = u.click_img_center(img_dicts['passwd'])
        if not pd_lc:
            return {'succ': False, 'msg': 'do not get password location'}
        # self.key_input(st=self.pwd, press_sleep=0.3)
        u.pag.typewrite(self.pwd, interval=0.3)     # 输入密码
        time.sleep(2)

        if not u.btn_location(img_dicts['btn_login']):  # 寻找登陆btn
            return {'succ': False, 'msg': 'do not get btn_login location'}

        # 滑块验证      path length: 248
        for x in range(4):
            u.click_img_center(img_dicts['btn_login'])      # 点击登录
            time.sleep(2)
            vc_location = u.btn_location(img_dicts.get('vc_block'), loop_time=3)
            if vc_location:                 # 寻找验证滑块
                self.slide_vc_block(vc_location)
            if not u.btn_location(img_dicts['btn_login']):  # 寻找登陆btn
                break
        else:   # 三次不通过就是失败
            return {'succ': False, 'msg': 'do not get btn_login location'}
        return {'succ': True}

    def login(self, ui):
        logger.info('delete_hosts:%s' % page_dict['delete_host_cookie'])
        self.acc, self.pwd = ui.get('account'), ui.get('password')
        self.sys_opera(page_dict['url'], delete_cookies=page_dict['delete_host_cookie'])
        try:
            # login process
            click_res = self.click_function()
            if not click_res['succ']:
                logger.warning(click_res['msg'])
                return click_res
            self.close_opera()
            cookies = self.getCookies(host=page_dict['host'], ck_type='json')
            if not cookies.get('succ'):
                logger.error(cookies.get('msg'))
                return {'succ': False}
            logger.info(cookies)
            return cookies
        except Exception as e:
            logger.error(e, exc_info=1)
            return {'succ': False, 'msg': e}
        finally:
            self.close_opera()

    def run_login(self, ui):
        for e in range(3):
            res = self.login(ui)
            if not res.get('succ'):
                continue
            return res
        else:
            # 上报无效
            # params = [ui.get('id'), ui.get('account'), ui.get('platform'), None, False]
            # if not post_res(*params):
            #     logger.error('----------useless account! Post result failed!')
            # else:
            logger.info('useless account!(%s) Post success!' % ui)
            return {'succ': False, 'invalid_account': True}


class AliyunSpider(TaskProcess):

    def __init__(self, user_info, **kwargs):
        global logger
        super().__init__(headers=base_header, user_info=user_info, **kwargs)
        self.child_accounts = None
        self.balance_data = []
        self.cookie_dict = None
        self.cookie_str = None
        self.cookie_list = None
        self.none_cost = None
        logger = self.logger

    def get_img(self, sd, ed, identity=None, company=None, pname=None):
        """截图，并处理图片文件"""
        # 截图
        if not pname:
            pname = '%(childAcc)s_#%(company)s_#%(sd)s_#%(ed)s.png' % {
                'childAcc': identity, 'company': company.strip(), 'sd': sd, 'ed': ed
            }
        else:
            pname = 'planName_#%s_#%s_#%s.png' % (pname, sd, ed)
        picname = join(self.dir_path, pname)
        cut_res = cut_img(None, self.dir_path, picname)
        if not cut_res.get('succ'):
            logger.error(cut_res.get('msg'))
            return {'succ': False}
        logger.info('got a pic: pic_name: %s' % picname)
        return {'succ': True}

    def get_child_accounts(self, reget=True, psize='20'):
        """获取子账号列表"""
        url = 'https://e.yunos.com/api/member/agency/ref/list?keyword=&page_size=%s&page=1' % psize
        headers = {'cookie': self.cookie_str, 'referer': 'https://e.yunos.com/'}
        self._headers.update(headers)
        data = get(url, headers=self._headers)
        if not data['is_success']:
            return {'succ': False, 'msg': data['msg']}
        data = json.loads(data['msg'].content.decode())
        if reget:
            total_count = data.get('total_count')
            return self.get_child_accounts(reget=False, psize=total_count)
        accounts = [(x['username'], x['company']) for x in data['data'] if x['status'] == 1 and x['privilege'] == 1 and x['ref_status'] == 1]
        self.child_accounts = accounts
        return {'succ': True, 'msg': accounts}

    def get_balance(self):
        res = self.get_child_accounts()
        if not res.get('succ'):
            raise Exception(res.get('msg'))
        for x in self.none_cost.copy():
            if self.none_cost.count(x) < 2:
                self.none_cost.remove(x)
        self.none_cost = list(set(self.none_cost))
        for acct, company in self.child_accounts:
            if acct not in self.none_cost:
                logger.info('skip has cost: %s' % acct)
                continue
            quote_acct = quote(acct)
            url = 'https://e.yunos.com/api/member/balance?identity=%s' % quote_acct
            ref = 'https://e.yunos.com/?identity=%s' % quote_acct
            res = self.deal_result(self.execute('GET', url, referer=ref), json_str=True)
            if not res.get('succ'):
                raise Exception(res.get('msg'))
            if not res.get('msg').get('success'):
                logger.error('balance res: %s' % res.get('msg'))
                return res
            balance = res.get('msg').get('data')/100
            bd = {'账号': acct, '账户余额': balance}
            logger.info(bd)
            self.balance_data.append(bd)

    def parse_balance(self, *args, **kwargs):
        header = ['账号', '账户余额']
        return header, self.balance_data

    def get_cid(self, identity):
        """
        获取组id
        :param identity: 子账号 需要编码
        :return: cid list
        """
        identity = quote(identity)
        url = 'https://e.yunos.com/api/campaign/list/layout?identity=%s' % identity
        headers = {
            "referer": "https://e.yunos.com/?identity=%s" % identity
        }
        self._headers.update(headers)
        data = get(url, headers=self._headers)
        if not data['is_success']:
            return {'succ': False, 'msg': data['msg']}
        data = json.loads(data['msg'].content.decode())
        cid = [x['id'] for x in data['data']] if data['total_count'] > 0 else []
        return {'succ': True, 'msg': cid}

    def get_data(self, c_cf, sd, ed, cid, identity, company, total_count=10, reget=True):
        """
        获取数据
        """
        # 处理文件名
        fname = '%(childAcc)s_#%(company)s_#%(sd)s_#%(ed)s.json' % {
            'childAcc': identity, 'company': company.strip(), 'sd': sd, 'ed': ed
        }
        file_name = join(self.dir_path, fname)
        if not cid:             # 没有数据, 没有产品
            return {'succ': False, 'msg': 'no data'}
        # 处理请求参数
        deal_identity = quote(identity)
        url = "https://e.yunos.com/api/rpt/list"
        param = {"page": 1, "page_size": total_count, "date_range_type": 0, "campaign_id": cid,
                 "report_level": 1, "report_data_type": 1, "start_ds": sd, "end_ds": ed}
        pdata = {'identity': deal_identity, 'param': json.dumps(param), 'p_cf': c_cf}

        # 发送请求
        data = post(url, data=pdata, headers=self._headers)
        if not data['is_success']:
            return {'succ': False, 'msg': data['msg']}
        # 获取数据总数
        data = data['msg'].content.decode('utf-8')
        t_count = int(json.loads(data).get('total_count'))
        if t_count == 0:        # 无消耗结算
            return {'succ': False, 'msg': 'no data'}
        if reget:
            return self.get_data(c_cf, sd, ed, cid, identity, company, total_count=t_count, reget=False)
        # 乱码整理
        data = json.loads(data)
        for i in data['data']:
            i['campaign_name'] = i.get('campaign_name').encode('gbk', 'ignore').decode('gbk')
        data = json.dumps(data)
        # 写入文件
        with open(file_name, 'w', encoding='gbk') as f:
            try:
                f.write(data)
            except Exception as e:
                logger.error(e, exc_info=1)
        logger.info('crawled data: --------' + data)
        return {'succ': True}

    def start_driver(self):
        self.init_browser()
        self.wait = WebDriverWait(self.d, 20)
        url = 'https://e.yunos.com/#/account/sub/list'
        self.d.get(url)
        self.d.delete_all_cookies()
        for e in self.cookie_list:
            self.d.add_cookie(e)
        time.sleep(1)
        self.d.get(url)
        time.sleep(1)

    def get_main_content(self, p_cf, cookie, sd, ed):
        # 获取主账号的数据，并且完成截图
        # get_data------ids
        url = 'https://e.yunos.com/api/campaign/list/layout'
        headers = {
            'accept': "application/json, text/javascript",
            'content-type': "application/x-www-form-urlencoded",
            'cookie': cookie,
            'referer': "https://e.yunos.com/",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
        }
        data = get(url, headers=headers)
        if not data.get('is_success'):
            return data
        id_list = json.loads(data.get('msg').content.decode('utf-8'))
        if id_list.get('total_count') == 0:
            return {'succ': False, 'msg': 'no data', 'account': self.acc}
        ids = [(e.get('id'), e.get('title')) for e in id_list.get('data') if '东方' in e.get('title')]
        # get_data------data
        filename = join(self.dir_path, 'mainContent_#%s_#%s.json' % (sd, ed))     # change file name
        url2 = 'https://e.yunos.com/api/rpt/list'
        payload = {
            'param': json.dumps({
                "page": 1, "page_size": 99999, "date_range_type": 0,
                "campaign_id": [i[0] for i in ids],
                "report_level": 1, "report_data_type": 1, "start_ds": sd, "end_ds": ed}),
            'p_cf': p_cf
        }
        data = post(url2, data=payload, headers=headers)
        if not data.get('is_success'):
            return {'succ': False, 'msg': data.get('msg')}
        data = json.loads(data.get('msg').content.decode('utf-8'))
        if data.get('total_count') == 0:
            return {'succ': False, 'msg': 'no data', 'account': self.acc}
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        return {'succ': True, 'msg': data, 'ids': ids, 'sd': sd, 'ed': ed}

    def get_plan_imgs(self, sd, ed, ids):
        url = 'https://e.yunos.com/#/reports/campaign'
        for e in range(3):
            try:        # 3次超时容错
                self.d.get(url)
                break
            except:
                continue
        else:
            return {'succ': False, 'msg': 'timeout after retried 3 times'}

        err_list = []
        # 更新日期
        self.update_date(sd, ed)
        time.sleep(2)
        # 跳转至主账号截图界面并且循环每个计划截图
        for i in ids:
            # 选择计划名（1，清空右侧计划，2，选择左侧对应计划）
            try:
                self.d.find_element_by_css_selector('.ant-transfer-list-body-not-found')
            except:
                logger.debug('ready to clear right menu list')
                clear_js = "document.querySelectorAll('.ant-transfer-checkbox-inner')[1].click()"
                self.d.execute_script(clear_js)
                self.wait_element(By.CLASS_NAME, 'anticon-left', ec=EC.element_to_be_clickable).click()

            # select plan from left memu
            eles = self.d.find_elements_by_class_name('custom-item')
            for e in eles:
                if e.text == i[1]:
                    e.click()
                    self.wait_element(By.CLASS_NAME, 'anticon-right', ec=EC.element_to_be_clickable).click()
                    break
            # 点击查看报表
            self.wait_element(By.CLASS_NAME, 'ant-btn-lg').click()
            # 开始截图
            res = self.get_img(sd, ed, pname=i[1])
            if not res.get('succ'):
                err_list.append(res)
        return err_list

    def get_data_process(self, dates):
        # 获取数据
        img_data, err_list, self.none_cost = [], [], []
        for sd, ed in dates:
            logger.info('data_range ---- %s~%s' % (sd, ed))
            """
            main_acc_res = self.get_main_content(cookie.get('c_cf'), cookie_str, sd, ed)           # 获取主账号数据
            if main_acc_res.get('succ'):
                main_acc_data.append((main_acc_res.get('sd'), main_acc_res.get('ed'), main_acc_res.get('ids')))
            """
            cac = self.get_child_accounts()   # 子账号列表
            if not cac['succ']:
                return cac
            logger.info('the length of child account:  %s' % len(cac['msg']))
            for ca, company in cac['msg']:           # 产品列表
                # if ca != '东方头条新闻':
                #     continue
                cids = self.get_cid(ca)
                if not cids['succ']:
                    err_list.append({'name': ca, 'hasData': None, 'sd': sd, 'ed': ed, 'img': False})
                    logger.error({'name': ca, 'hasData': None, 'sd': sd, 'ed': ed, 'img': False, 'msg': cids['msg']})
                    # logger.error(cids['msg'])
                res = None
                try:
                    res = self.get_data(self.cookie_dict['c_cf'], sd, ed, cids['msg'], ca, company)    # 数据
                except Exception as er:
                    logger.error(er, exc_info=1)
                    logger.error(res)
                    logger.error({'acc': self.acc, 'name': ca, 'hasData': None, 'sd': sd, 'ed': ed})
                    continue
                if res['succ']:
                    img_data.append({'name': ca, 'company': company, 'hasData': True, 'sd': sd, 'ed': ed, 'img': False})
                elif not res['succ'] and res['msg'] == 'no data':
                    res_dict = {'name': ca, 'company': company, 'hasData': False}
                    self.none_cost.append(ca)
                    img_data.append(res_dict)
                    logger.warning({'name': ca, 'hasData': False, 'sd': sd, 'ed': ed})
                else:
                    err_list.append({'name': ca, 'hasData': None, 'sd': sd, 'ed': ed, 'img': False})
                    logger.error(res['msg'])        # 请求失败(网络问题)
        return img_data, err_list

    def login_part(self, ui, **kwargs):
        # 登陆
        self.login_obj = LoginAlios()
        return self.login_obj.run_login(ui)

    def deal_login_result(self, login_res):
        if not login_res['succ']:
            return {'succ': False, 'msg': login_res.get('msg', 'None msg in return dict')}
        self.cookie_dict = {e.get('name'): e.get('value') for e in login_res['msg']}
        self.cookie_str = '; '.join(['%s=%s' % (k, v) for k, v in self.cookie_dict.items()])
        self.cookie_list = login_res.get('msg')

    def get_data_part(self, *args, **kwargs):
        # 获取时间
        ys, ms, ye, me = self.user_info.get('dates') if self.user_info.get('dates') else (None, None, None, None)
        mths, dates = u.make_dates(ys=ys, ms=ms, ye=ye, me=me)
        img_data, err_list = self.get_data_process(dates)       # 获取数据
        # 是否有数据
        has_data = [1 for x in img_data if x.get('hasData')]
        if len(has_data) == 0:
            self.result_kwargs['has_data'] = 0
        self.get_account_balance()
        return img_data, err_list

    def get_img_part(self, img_data, err_list):
        # 依据数据有无进行截图
        self.start_driver()
        for i in img_data:
            if i.get('hasData'):
                try:
                    res = self.to_img_page(i['name'], i['company'], i['sd'], i['ed'])
                    if not res.get('succ', False):
                        i['img'] = True
                        err_list.append(i)
                        logger.error(res.get('msg'))
                except Exception as e:
                    logger.error(e, exc_info=1)
        else:
            logger.warning(err_list)
            self.d.quit()

    def get_data_and_imgs(self, *args, **kwargs):
        res = self.get_data_part(*args, **kwargs)
        if self.result_kwargs.get('has_data') == 0:
            return
        if not self.is_get_img:
            return
        self.get_img_part(*res)

    def update_date(self, sd, ed):
        self.d.find_elements_by_class_name('ant-radio-input')[-1].click()
        self.wait_element(By.CLASS_NAME, 'ant-calendar-range-picker').click()
        self.wait_element(By.XPATH, "//div[@class='ant-calendar-date-input-wrap']/input[@placeholder='开始日期']").clear()
        self.wait_element(By.XPATH, "//div[@class='ant-calendar-date-input-wrap']/input[@placeholder='开始日期']").send_keys(sd)
        try:
            self.wait_element(By.CLASS_NAME, 'ant-calendar-range-picker').click()
        except:
            logger.debug("didn't disappear, pass")
        self.wait_element(By.XPATH, "//div[@class='ant-calendar-date-input-wrap']/input[@placeholder='结束日期']").clear()
        self.wait_element(By.XPATH, "//div[@class='ant-calendar-date-input-wrap']/input[@placeholder='结束日期']").send_keys(ed)
        time.sleep(0.5)

    def to_img_page(self, account, company, sd, ed):
        url = 'https://e.yunos.com/?identity=%s#/reports/campaign' % account
        self.d.get(url)
        time.sleep(3)
        self.d.find_element_by_class_name('ant-transfer-checkbox-inner').click()
        time.sleep(1)
        try:
            self.d.find_element_by_class_name('anticon-right').click()
        except:
            # 无数据消耗, 直接截图
            logger.info('no spend, turn to cut img')
        time.sleep(1)
        # 调整日期
        try:
            self.update_date(sd, ed)
        except Exception as e:
            logger.error(e, exc_info=1)
            return {'succ': False, 'msg': e}
        # 点击查看报表
        self.d.find_element_by_class_name('ant-btn-lg').click()
        # 开始截图
        return self.get_img(sd, ed, identity=account, company=company)

