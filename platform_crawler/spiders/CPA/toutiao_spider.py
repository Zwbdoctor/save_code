"""
cpa 头条系 爬虫 ---- https://pangolin.bytedance.com/auth/login
"""
from json import dump, dumps
import os
import time
import requests

from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.by import By
from pyautogui import hotkey, typewrite

from platform_crawler.spiders.pylib.task_process import TaskProcess
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.utils.utils import Util
from platform_crawler.settings import IMG_PATH, join



u = Util()
logger = None


class LoginTouTiao:

    def __init__(self, ui):
        self.d = None
        self.wait = None
        self.user_info = ui
        self.acc, self.pwd = ui.get('account'), ui.get('password')
        # super().__init__(headers=base_header, spider=ui.get('platform'))

    def init_browser(self):
        from selenium import webdriver
        self.d = webdriver.Chrome()
        self.d.delete_all_cookies()
        self.d.set_page_load_timeout(60)
        self.d.set_script_timeout(60)
        self.d.maximize_window()
        self.wait = WebDriverWait(self.d, 20)

    def waitElement(self, element_type, wait_sth):
        ele = self.wait.until(EC.visibility_of_element_located((element_type, wait_sth)))
        return ele

    def is_login(self):
        cookie = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in self.d.get_cookies()])
        url = 'https://pangolin.bytedance.com/api/checking_page'
        headers = {
            'accept': "application/json",
            'content-type': "application/json",
            'cookie': cookie,
            # 'referer': "https://pangolin.bytedance.com/",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3569.0 Safari/537.36",
        }
        # res = self.deal_result(self.execute('POST', url, data='', headers=headers, verify=False), json_str=True)
        try:
            res = requests.post(url, data='', headers=headers, timeout=60, verify=False)
        except Exception as e:
            logger.error(e, exc_info=1)
            return {'succ': False, 'msg': e}
        try:
            res_status = res.json()
        except:
            return {'succ': False, 'msg': 'login failed'}
        if res.status_code != 200:
            return {'succ': False, 'msg': 'status code is not 200'}
        if res_status.get('message') == 'success':
            logger.info('login success')
            return {'succ': True, 'headers': headers}
        return {'succ': False, 'msg': res_status.get('msg')}

    def run(self):
        for e in range(3):
            try:
                self.d.get('https://pangolin.bytedance.com/auth/login')
                self.d.implicitly_wait(10)
                break
            except:
                continue
        self.wait.until(EC.visibility_of_element_located((By.ID, 'username'))).send_keys(self.acc)
        self.wait.until(EC.visibility_of_element_located((By.ID, 'password'))).send_keys(self.pwd)
        vc_img = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'img')))
        vc_path = join(IMG_PATH, 'vc.png')
        u.cutimg_by_driver(self.d, vc_img, vc_path)
        with open(vc_path, 'br') as i:
            im = i.read()
        vc_obj = u.rc.rk_create(im, 3040)
        vc = vc_obj.get('Result').lower()
        self.wait.until(EC.visibility_of_element_located((By.ID, 'captcha'))).send_keys(vc)
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.ant-btn-lg'))).click()
        self.d.implicitly_wait(15)
        time.sleep(3)
        login_res = self.is_login()
        if not login_res.get('succ'):
            login_status = self.d.find_element_by_class_name('ant-confirm-content').text.strip()
            if login_status == '登录失败':
                logger.warning('account or password wrong')
                return {'succ': False, 'msg': 'wrong pwd or account'}
            elif login_status == '验证码错误':
                logger.warning('verify code wring')
                u.rc.rk_report_error(vc_obj.get('Id'))
                return self.run()
        u.rc.rk_report(im, 3040, vc, vc_type=self.user_info.get('platform'))
        return login_res

    def run_login(self):
        self.init_browser()
        for i in range(3):
            try:
                res = self.run()
                if res.get('succ'):
                    res['driver'] = self.d
                    return res
            except Exception as er:
                logger.error(er, exc_info=1)
                continue
        else:
            # params = [self.user_info.get('id'), self.user_info.get('account'), self.user_info.get('platform'), None,
            #           False]
            # if not post_res(*params):
            #     logger.error('----------useless account! Post result failed!')
            # else:
            logger.info('useless account!(%s) Post success!' % self.user_info.get('account'))
            self.d.quit()
            return {'succ': False, 'invalid_account': True}


class TouTiaoSpider(TaskProcess):

    def __init__(self, user_info, **kwargs):
        global logger
        self.cookies = {}
        self.acc = user_info.get('account')
        self.platform = user_info.get('platform')
        super().__init__(is_cpa=True, user_info=user_info, **kwargs)
        logger = self.logger

    def get_data_process(self, sd, ed):
        file_name = '%s_%s.json' % (sd, ed)
        res = self.get_data(sd, ed)
        if not res.get('succ'):
            return res
        data = res.get('msg')
        if not data:
            data = {'msg': 'no data'}
        with open(os.path.join(self.dir_path, file_name), 'w', encoding='utf-8') as f:
            dump(data, f)
        return {'succ': True}

    def get_data(self, sd, ed, content=None, pn=None):
        url = "https://pangolin.bytedance.com/api/activation/list"
        p = 1 if not pn else pn
        payload = {
            "search": {"DateStart": sd, "DateEnd": ed, "AppId": "", "ChannelName": "", "OS": ""},
            "page": {"p": p}}
        res = self.deal_result(self.execute('POST', url, data=dumps(payload), verify=False), json_str=True)
        if not res.get('succ') and not res.get('msg').get('message') == 'success':
            return res
        data = content if isinstance(content, list) else []
        dat = res.get('msg').get('data').get('list')
        page = res.get('msg').get('data').get('page')
        p = page.get('Next')
        data.extend(dat)
        logger.debug(dat)
        logger.info('--- Page ---  --- %s/%s ---' % (page.get('PageNo'), page.get('MaxPage')))
        if page.get('Next') == 0:
            return {'succ': True, 'msg': data}
        if page.get('PageNo') != page.get('MaxPage'):
            return self.get_data(sd, ed, content=data, pn=p)
        # return {'succ': True, 'msg': data}

    def get_channels(self):
        url = 'https://pangolin.bytedance.com/api/search/external_default'
        res = self.deal_result(self.execute('GET', url), json_str=True)
        if not res.get('succ'):
            return res
        channel_list = res.get('msg').get('data').get('ChannelNameList')
        return channel_list

    def get_img(self, sd, ed, channels):
        channels = [] if not channels else channels
        for c in channels:
            self.d.find_element_by_class_name('ant-select-search__field__wrap').click()
            hotkey('ctrl', 'a')
            typewrite(c.get('Name'))
            self.d.find_element_by_class_name('ant-btn-primary').click()
            self.d.implicitly_wait(5)
            time.sleep(1)
            # while True:
            self.d.execute_script('document.querySelector("#root").scrollTop = 0')
            pic_name = '%s_%s_%s.png' % (c.get('Name'), sd, ed)
            height = self.d.execute_script('return a=document.body.offsetHeight')
            cut_res = cut_img(height, self.dir_path, pic_name)
            if not cut_res.get('succ'):
                logger.error('got pic failed  ---  pic_name: %s' % pic_name)
            # next_page_dis = self.d.find_element_by_css_selector('li[title="下一页"]').get_attribute('aria-disabled')
            # if next_page_dis != 'false':
            #     break
            # self.d.find_element_by_css_selector('li[title="下一页"]').click()
            # time.sleep(1)
            # self.d.find_element_by_css_selector('span.ant-spin-dot').click()

    def change_date(self, sd, ed):
        from selenium.webdriver.common.action_chains import ActionChains
        ac = ActionChains(self.d)
        self.d.execute_script('document.querySelector("#root").scrollTop = 0')
        self.wait_element(By.CSS_SELECTOR, 'span.ant-input').click()
        sd_box = self.wait_element(By.XPATH, '//input[@placeholder="开始日期"]')
        ed_box = self.wait_element(By.XPATH, '//input[@placeholder="结束日期"]')
        ac.move_to_element_with_offset(sd_box, 5, 5).click().perform()
        hotkey('ctrl', 'a')
        typewrite(sd)
        time.sleep(1)
        # self.wait_element(By.CSS_SELECTOR, 'span.ant-input').click()
        ac.move_to_element_with_offset(ed_box, 80, 5).click().perform()
        hotkey('ctrl', 'a')
        typewrite(ed)
        # self.wait_element(By.CSS_SELECTOR, 'span.ant-spin-dot', EC.invisibility_of_element_located)

    def login_and_get_data(self, ui):
        lu = LoginTouTiao(ui).run_login()
        if not lu.get('succ'):
            return lu
        self.d = lu.get('driver')
        self.wait = WebDriverWait(self.d, 20)
        self._headers = lu.get('headers')

        mths, dates = u.make_dates(ys=None, ms=None, ye=None, me=None)
        for sd, ed in dates:
            ed = ed.replace('31', '30')
            data_res = self.get_data_process(sd, ed)
            if not data_res.get('succ'):
                return data_res

        channel_list = self.get_channels()
        self.d.get('https://pangolin.bytedance.com/active-statistic')
        self.d.implicitly_wait(30)
        for sd, ed in dates:
            ed = ed.replace('31', '30')
            self.change_date(sd, ed)
            self.get_img(sd, ed, channel_list)
            time.sleep(2)
        self.d.quit()
        return {'succ': True}
