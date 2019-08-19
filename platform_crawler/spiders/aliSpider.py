from platform_crawler.spiders.get_login_data.BaseModel import Base
from configs.aliyun_config import page_dict, img_dicts
from platform_crawler.utils.scp_tool import RemoteShell
from platform_crawler.utils.post_get import post, get
from platform_crawler.utils.utils import Util

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from urllib.parse import quote
from subprocess import Popen
import time
import os
# import pickle
# import traceback
import json

ask_sql_url = 'http://erp.btomorrow.cn/adminjson/adminjson/ERP_GetCrawlerTaskStatus'   # useless
post_res_url = 'http://erp.btomorrow.cn/adminjson/ERP_ReportPythonCrawlerTask'
fscapture = r'D:\fscapture\FSCapture.exe'

u = Util()
img_temp_path = os.path.join(os.path.abspath('.'), 'img_temp\\')
log_path = os.path.abspath('./logs/Alios')
if not os.path.exists(log_path):
    os.makedirs(log_path)
save_path = os.path.abspath('./save_data')


logger = u.record_log(log_path, __name__)

real_ip = '139.224.116.116'
serv_parm = {
    'ip': real_ip, 'user': 'root', 'pwd': 'hhmt@pwd@123', 'dst_path': ''
}


class AliyunSpider(Base):

    def __init__(self, user_info):
        self.dst_path = '/data/python/%s/' % user_info['platform']
        self.dir_path = None
        self.line_path = None
        self.acc = user_info['account']
        self.pwd = user_info['password']
        self.page_dict = page_dict
        self.img_dicts = img_dicts
        self.d = None
        self.wait = None
        super().__init__()
        self.init__post_param()

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

    def mDays(self, year, month):
        d30 = [4, 6, 9, 11]
        d31 = [1, 3, 5, 7, 8, 10, 12]
        m2 = 29 if year/4 == 0 and year/4 != 0 else 28
        if month in d30:
            days = 30
        elif month in d31:
            days = 31
        else:
            days = m2
        return days

    def get_date(self, year, m):
        """
        v1: # 平移60天
        current_date = time.strftime('%Y-%m-%d')
        year, month, day = (int(e) for e in time.strftime('%Y-%m-%d').split('-'))
        lm = mDays(year, month-1)
        llm = mDays(year, month-2)
        sd = llm-(60-lm-month)
        v2:
        """
        z = lambda x:  x if len(str(x)) == 2 else '0%s' % x
        end = self.mDays(year, m)
        start = '%s-%s-01' % (year, z(m))
        end = '%s-%s-%s' % (year, z(m), end)
        return start, end

    def move_img(self, picname, fs):
        """移动图片"""
        try:
            st = time.time()
            while True:
                f_list = os.listdir(img_temp_path)
                if f_list:
                    fs.kill()
                    time.sleep(0.5)
                    with open(os.path.join(img_temp_path, f_list[0]), 'br') as old:
                        oi = old.read()
                    with open(os.path.join(self.dir_path, picname), 'bw') as newf:
                        newf.write(oi)
                    return True
                elif time.time() - st > 6:      # 超过5秒没得到
                    return False
        except Exception as e:
            logger.error(e, exc_info=1)
            return False

    def clear_imgs(self):
        f_list = os.listdir(img_temp_path)
        if f_list:
            for e in f_list:
                os.remove(img_temp_path + e)

    def get_img(self, sd, ed, identity=None, company=None, pname=None):
        """截图，并处理图片文件"""
        # 清除可能存在的图片
        self.clear_imgs()
        # 截图
        fs = Popen([fscapture])
        # self.key_group(['alt', 'print_screen'])
        u.pag.hotkey('alt', 'prtsc', interval=0.3)
        time.sleep(2)

        if not pname:
            pname = '%(childAcc)s_#%(company)s_#%(sd)s_#%(ed)s.png' % {
                'childAcc': identity, 'company': company.strip(), 'sd': sd, 'ed': ed
            }
        else:
            pname = 'planName_#%s_#%s_#%s.png' % (pname, sd, ed)
        picname = os.path.join(self.dir_path, pname)
        if not self.move_img(picname, fs):
            return {'succ': False, 'msg': 'get img %s failed' % pname}
        return {'succ': True}

    def wait_element(self, ele_type, ele, ec=EC.presence_of_element_located):
        try:
            ele = self.wait.until(ec((ele_type, ele)))
            return ele
        except:
            return False

    def click_function(self):
        un_lc = self.u.click_img_center(self.img_dicts['user_name'])
        if not un_lc:
            logger.warning('do not get user_name location')
            return {'succ': False, 'msg': 'do not get user_name location'}
        time.sleep(1)
        self.key_input(st=self.acc, press_sleep=0.3)
        time.sleep(2)
        self.u.pag.click(140, 115)

        pd_lc = self.u.click_img_center(self.img_dicts['passwd'])
        if not pd_lc:
            return {'succ': False, 'msg': 'do not get password location'}
        self.key_input(st=self.pwd, press_sleep=0.3)
        time.sleep(2)

        login_btn = self.u.click_img_center(self.img_dicts['btn_login'])
        if not login_btn:
            return {'succ': False, 'msg': 'do not get btn_login location'}
        time.sleep(3)
        return {'succ': True}

    def login(self):
        logger.info('delete_hosts:')
        logger.info(self.page_dict['delete_host_cookie'])
        self.base_login('sys')
        try:
            # login process
            click_res = self.click_function()
            if not click_res['succ']:
                logger.warning(click_res['msg'])
                return click_res
            self.close_opera()
            cookies = self.getCookies(ck_type='json')
            logger.info(cookies)
            return {'succ': True, 'msg': cookies}
        except Exception as e:
            logger.error(e, exc_info=1)
            return {'succ': False, 'msg': e}
        finally:
            self.close_opera()

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
        self.headers.update(headers)
        data = get(url, headers=self.headers)
        if not data['is_success']:
            return {'succ': False, 'msg': data['msg']}
        data = json.loads(data['msg'].content.decode())
        cid = [x['id'] for x in data['data']] if data['total_count'] > 0 else []
        return {'succ': True, 'msg': cid}

    def get_data(self, c_cf, sd, ed, cid, identity, company, total_count=10, reget=True):
        """
        获取数据
        :param cookie: a list of cookie[{}, {}]
        :param cid: a list of group id
        :return:
        """
        # 处理文件名
        fname = '%(childAcc)s_#%(company)s_#%(sd)s_#%(ed)s.json' % {
            'childAcc': identity, 'company': company.strip(), 'sd': sd, 'ed': ed
        }
        file_name = os.path.join(self.dir_path, fname)
        if not cid:             # 没有数据, 没有产品
            with open(file_name, 'w') as f:
                f.write('{"msg": "no data"}')
            return {'succ': False, 'msg': 'no data'}
        # 处理请求参数
        deal_identity = quote(identity)
        url = "https://e.yunos.com/api/rpt/list"
        param = {"page": 1, "page_size": total_count, "date_range_type": 0, "campaign_id": cid,
                 "report_level": 1, "report_data_type": 1, "start_ds": sd, "end_ds": ed}
        pdata = {'identity': deal_identity, 'param': json.dumps(param), 'p_cf': c_cf}

        # 发送请求
        data = post(url, data=pdata, headers=self.headers)
        if not data['is_success']:
            return {'succ': False, 'msg': data['msg']}
        # 获取数据总数
        data = data['msg'].content.decode('utf-8')
        t_count = int(json.loads(data).get('total_count'))
        if t_count == 0:        # 无消耗结算
            with open(file_name, 'w') as f:
                f.write('{"msg": "no data"}')
            return {'succ': False, 'msg': 'no data'}
        if reget:
            time.sleep(0.25)
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
                # json.dump(data, f)
            except Exception as e:
                logger.error(e, exc_info=1)
        logger.info('crawled data: --------' + data)
        return {'succ': True}

    def upload_file(self):
        global serv_parm
        cudate = time.strftime('%Y-%m-%d')
        serv_parm['dst_path'] = self.dst_path + cudate + '/'
        files = os.listdir(self.dir_path)
        if not files:
            with open(os.path.join(self.dir_path, 'no_data'), 'w') as f:
                f.write('no data')
        t = RemoteShell(serv_parm['ip'], serv_parm['user'], serv_parm['pwd'])
        if not t.put(self.dir_path, serv_parm['dst_path']):
            logger.error('upload failed ----acc:%s--pwd:%s' % (self.acc, self.pwd))
            return False
        return True

    def make_days(self, ms=None, ys=None, mee=None, ye=None):
        """
        生成一段时间中，每个月的开始和结束日期
        :param ms: start month
        :param ys: start year
        :param mee: end month
        :param ye: end year
        :return: a list [(startdate, enddate),()]
        """
        mths = []
        year, month, cDay = time.strftime('%Y-%m-%d').split('-')
        ms = int(month)-1 if not ms else ms  # 开始月份 defaul: 前一个月
        ys = int(year) if not ys else ys
        ye = int(year) if not ye else ye
        mee = int(month) if not mee else mee
        med = 13      # month end default
        for y in range(ys, ye+1):
            if y == ye:  # 控制结束月份
                med = mee + 1
            for m in range(ms, med):
                mths.append((y, m))
            ms = 1
        z = lambda x: x if len(str(x)) == 2 else '0%s' % x
        dates = []
        for y, m in mths:
            if y == int(year) and m == int(month):
                dates.append(('%s-%s-01' % (y, z(m)), '%s-%s-%s' % (y, z(m), z(cDay))))
            else:
                dates.append(self.get_date(y, m))
        return dates

    def start_driver(self, cookie):
        self.d = self.init_driver()
        self.wait = WebDriverWait(self.d, 20)
        url = 'https://e.yunos.com/#/account/sub/list'
        self.d.get(url)
        self.d.delete_all_cookies()
        for e in cookie['msg']:
            self.d.add_cookie(e)
        time.sleep(1)
        self.d.get(url)
        time.sleep(1)

    def init_dst_dir(self):
        cudate = time.strftime('%Y-%m-%d')
        dst_name = self.dst_path + cudate + '/'
        t = RemoteShell(serv_parm['ip'], serv_parm['user'], serv_parm['pwd'])
        if not t.put(os.path.abspath('./init_dir'), dst_name):
            logger.error('init dst dir failed ----acc:%s--pwd:%s' % (self.acc, self.pwd))
            return {'succ': False, 'msg': 'init dst dir failed'}
        return {'succ': True}

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
        filename = os.path.join(self.dir_path, 'mainContent_#%s_#%s.json' % (sd, ed))     # change file name
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

    def run(self, ui):
        # 创建文件夹
        cutime = time.strftime('%Y-%m-%d')
        dir_name = '%(taskId)s_%(cTime)s_%(account)s' % {'taskId': ui['id'], 'cTime': time.strftime('%Y-%m-%d_%H-%M-%S'),
                                                         'account': self.acc}
        self.dir_path = os.path.join(os.path.abspath('./save_data/%s' % ui['platform']), cutime, dir_name)
        os.makedirs(self.dir_path)
        # 登陆
        first_cookie = self.login()
        if not first_cookie['succ']:
            return {'succ': False, 'msg': first_cookie['msg']}

        """
        first_cookie = {'msg': [
            {'domain': 'e.yunos.com', 'name': 'c_cf', 'path': '/', 'value': '6c0cb921-8dda-4c83-8ba9-028f6c0a7d42'},
            {'domain': '.yunos.com', 'name': 'cna', 'path': '/', 'value': 'CKwPFBb6HhUCAXFXek3ktBZe'},
            {'domain': '.yunos.com', 'name': 'isg', 'path': '/',
             'value': 'BJubrBVvROaI5bgSbEfU4GQgKv_F2Kz3R67c_I3YdxqxbLtOFEA_wrmtAozHzAdq'},
            {'domain': '.yunos.com', 'name': 'login_yunos_ticket', 'path': '/',
             'value': '84fd5dbf55cbebf92b8aa19b3df74378859aee24eabef4da8628c081f06ed685'},
            {'domain': '.yunos.com', 'name': 'login_yunosid', 'path': '/',
             'value': '01%E8%BE%89%E7%85%8C%E6%98%8E%E5%A4%A9'},
            {'domain': '.yunos.com', 'name': 'session_id', 'path': '/', 'value': '1539576141179y1DluJ35S1C'}
        ]}
        """
        # 获取时间
        ys, ms, ye, me = ui.get('dates') if ui.get('dates') else (None, None, None, None)
        mths, dates = u.make_dates(ys=ys, ms=ms, ye=ye, me=me)
        # dates = self.make_days(ys=None, ms=None, ye=None, mee=None)
        cookie = {e['name']: e['value'] for e in first_cookie['msg']}
        cookie_str = '; '.join(['%s=%s' % (k, v) for k, v in cookie.items()])   # 处理cookie

        # 获取数据
        img_data = []
        err_list = []
        # main_acc_data = []
        start_time = time.time()
        for sd, ed in dates:
            logger.info('data_range ---- %s~%s' % (sd, ed))
            """
            main_acc_res = self.get_main_content(cookie.get('c_cf'), cookie_str, sd, ed)           # 获取主账号数据
            if main_acc_res.get('succ'):
                main_acc_data.append((main_acc_res.get('sd'), main_acc_res.get('ed'), main_acc_res.get('ids')))
            """
            cac = self.get_child_accounts(cookie_str)   # 子账号列表
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
                    res = self.get_data(cookie['c_cf'], sd, ed, cids['msg'], ca, company)    # 数据
                except Exception as er:
                    logger.error(er, exc_info=1)
                    logger.error(res)
                    logger.error({'acc': self.acc, 'name': ca, 'hasData': None, 'sd': sd, 'ed': ed})
                    continue
                if res['succ']:
                    img_data.append({'name': ca, 'company': company, 'hasData': True, 'sd': sd, 'ed': ed, 'img': False})
                elif not res['succ'] and res['msg'] == 'no data':
                    img_data.append({'name': ca, 'company': company, 'hasData': False, 'img': False})
                    logger.warning({'name': ca, 'hasData': False, 'img': False, 'sd': sd, 'ed': ed})
                else:
                    err_list.append({'name': ca, 'hasData': None, 'sd': sd, 'ed': ed, 'img': False})
                    logger.error(res['msg'])        # 请求失败(网络问题)
                time.sleep(0.25)
        self.start_driver(first_cookie)
        """
        for sd, ed, ids in main_acc_data:
                self.get_plan_imgs(sd, ed, ids)
        """
        for i in img_data:
            if i['hasData']:
                try:
                    res = self.to_img_page(i['name'], i['company'], i['sd'], i['ed'])
                    if not res['succ']:
                        i['img'] = True
                        # i['msg'] = res['msg']
                        err_list.append(i)
                        logger.error(res['msg'])
                except Exception as e:
                    logger.error(e, exc_info=1)
        else:
            logger.warning(err_list)
            self.d.quit()
        logger.info('crawled 2 months data use time : -----%d' % int(time.time()-start_time))

        # 上传
        if not self.upload_file():
            return {'succ': False, 'msg': 'upload failed'}
        return {'succ': True, 'data_path': '%s/%s' % (cutime, dir_name)}

    def update_date(self, sd, ed):
        self.d.find_elements_by_class_name('ant-radio-input')[-1].click()
        self.wait_element(By.CLASS_NAME, 'ant-calendar-range-picker').click()
        self.wait_element(By.XPATH, "//div[@class='ant-calendar-date-input-wrap']/input[@placeholder='开始日期']").clear()
        self.wait_element(By.XPATH, "//div[@class='ant-calendar-date-input-wrap']/input[@placeholder='开始日期']").send_keys(sd)
        # self.d.find_element_by_css_selector('body').click()
        # time.sleep(1)
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


class TaskProcess:

    def __init__(self, data):
        pass

    def post_res(self, data):
        data = json.dumps(data)
        res = post(post_res_url, data=data, headers={'Content-Type': 'application/json'})
        if not res['is_success']:
            # 上报失败
            return False
        else:
            # 上报成功
            logger.info('Post success! ret_msg: ' + res['msg'].content.decode('utf-8'))
            return True

    def get_pwd(self, plaintext):
        """
        DES 解密
        :param s: 加密后的字符串，16进制
        :return:  解密后的字符串
        """
        import binascii
        from pyDes import des, CBC, PAD_PKCS5
        secret_key = '%$#(*N@M'
        iv = secret_key
        k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
        de = k.decrypt(binascii.a2b_hex(plaintext), padmode=PAD_PKCS5).decode()
        return de

    def run_task(self, um):
        # um['password'] = self.get_pwd(um['password'].encode('utf-8'))
        um['password'] = self.get_pwd(um['password'])
        app = AliyunSpider(um)
        app.init_dst_dir()
        for e in range(1, 5):      # 4次容错
            um['line_num'] = e
            res = app.run(um)
            if not res['succ']:
                logger.error('----------Failed %s times:' % e)
                logger.error('----------errorMsg: ---------')
                logger.error(res['msg'])
                continue
            else:
                # 通报服务器
                post_data = {'taskId': um['id'], 'status': 3, 'statusDesc': '成功', 'account': um['account'],
                             'platform': um['platform'], 'filePathCatalog': None}
                if res.get('msg') == 'no data':
                    post_data['statusDesc'] = '没有数据'
                else:
                    post_data['filePathCatalog'] = res['data_path']
                logger.info('Post Data:')
                logger.info(post_data)
                if not self.post_res(post_data):
                    logger.error('----------after upload files, post result failed !!!!')
                    return False
                else:
                    logger.info('Upload success! Post result success!')
                    return True
        else:
            # 无效用户，上报无效结果
            post_data = {'taskId': um['id'], 'errorCode': 10000, 'status': 4, 'statusDesc': '账号无效', 'account': um['account'],
                         'platform': um['platform'], 'filePathCatalog': ''}
            if not self.post_res(post_data):
                logger.error('----------useless account! Post result failed!')
                return False
            else:
                logger.info('useless account!(%s) Post success!' % um['account'])
                return True


