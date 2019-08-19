'''
http://tg.app.sogou.com/
'''
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.spiders.pylib.task_process import TaskProcess
import requests
from platform_crawler.utils.utils import Util
import json
import os
import time


u = Util()
logger = None
g_product_a = 'SGSJZS'
g_product_b = 'SGBrowser'


class SogouSpider(TaskProcess):
    def __init__(self, user_info, **kwargs):
        global logger
        super().__init__(is_cpa=True, user_info=user_info, **kwargs)
        logger = self.logger

    def login(self):
        self.d.get('http://tg.app.sogou.com/')
        prdSel = self.wait_element(By.CSS_SELECTOR, 'select[name="product"]')
        prdSel = Select(prdSel)
        if self.user_info.get('platform') == g_product_a:
            prdSel.select_by_value('A')
        elif self.user_info.get('platform') == g_product_b:
            prdSel.select_by_value('B')

        inpUsername = self.d.find_element_by_id('username')
        inpUsername.clear()
        inpUsername.send_keys(self.acc)
        inpPassword = self.d.find_element_by_id('password')
        inpPassword.clear()
        inpPassword.send_keys(self.pwd)
        btnLogin = self.d.find_element_by_css_selector('input[value="登录"]')
        btnLogin.click()
        self.d.implicitly_wait(5)
        time.sleep(2)

        self.d.switch_to.frame('topFrame')
        logout = self.d.find_element_by_css_selector('.logout a').text
        if logout == 'LOGOUT':
            ck = self.d.get_cookies()
            return {'succ': True, 'cookies': ck}
        else:
            return {'succ': False}

    # 登录重试
    def runLogin(self):
        for e in range(1, 5):
            self.init_browser()
            res = self.login()
            if res['succ']:
                return res
            else:
                self.d.quit()
        else:
            # 上报无效
            # params = [self.user_info.get('id'), self.user_info.get('account'), self.user_info.get('platform'), None, False]
            # if not post_res(*params):
            #     logger.error('----------useless account! Post result failed!')
            # else:
            logger.info('useless account!(%s) Post success!' % self.user_info)
            
            self.d.quit()
            return {'succ': False, 'invalid_account': True}

    def change_date(self, sd, ed):
        self.wait_element(By.ID, 'startdate')
        self.d.execute_script('document.querySelector("#startdate").value="%s"' % sd)
        self.d.execute_script('document.querySelector("#enddate").value="%s"' % ed)

    def get_img(self, sd, ed, pids):
        self.change_date(sd, ed)
        if not pids:
            self.wait_element(By.ID, 'searchData').click()
            text = self.wait_element(By.ID, 'content').text
            if text.strip() == '该时间段无数据':
                logger.info('dataRange: %s ~ %s--- has no data' % (sd, ed))
                return
            height = self.d.execute_script('return document.documentElement.offsetHeight')
            pic_name = '%s_%s.png' % (sd, ed)
            # cut_res = cut_img(height, self.dir_path, pic_name, click_point=[910, 470])
            cut_res = cut_img(height, self.dir_path, pic_name)
            if not cut_res['succ']:
                logger.error('cut picture failed, possible msg:\ndir_path:%s\npic_name: %s' % (self.dir_path, pic_name))
            logger.info('got a picture: pic_msg: %s' % os.path.join(self.dir_path, pic_name))
            return

        for pid in pids:
            self.d.execute_script('document.documentElement.scrollTop=0')
            self.d.execute_script('''document.querySelector('select[name="pid"]').value="%s"''' % pid)
            self.wait_element(By.ID, 'searchData').click()
            text = self.wait_element(By.ID, 'content').text
            if text.strip() == '该时间段无数据':
                logger.info('channel: %s -- dataRange: %s ~ %s--- has no data' % (pid, sd, ed))
                continue
            height = self.d.execute_script('return document.documentElement.offsetHeight')
            pic_name = '%s_%s_%s.png' % (pid, sd, ed)
            cut_res = cut_img(height, self.dir_path, pic_name)
            if not cut_res['succ']:
                logger.error('cut picture failed, possible msg:\ndir_path:%s\npic_name: %s' % (self.dir_path, pic_name))
            logger.info('got a picture: pic_msg: %s' % os.path.join(self.dir_path, pic_name))

    def get_data(self, cookie, osd, oed):
        logger.info('get_data|start osd:%s oed:%s' %(osd, oed))
        ckstr = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in cookie])
        headers = {
            'Cookie': ckstr,
            'Referer': 'http://tg.app.sogou.com/common.php?action=dataPerday',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
        }
        product, url = None, None
        if self.user_info.get('platform') == g_product_a:
            product = 'A'
            url = r'http://tg.app.sogou.com/data.php?action=getData&startdate=%s&enddate=%s&order=date&isdesc=DESC' % (osd, oed)
        elif self.user_info.get('platform') == g_product_b:
            product = 'B'
            url = r'http://tg.app.sogou.com/data.php?action=getData&startdate=%s&enddate=%s&order=date&isdesc=DESC&pid=&product=%s' % (osd, oed, product)
        logger.info('get_data|request start: %s' % url)
        try:
            res = requests.get(url, headers=headers)
            if res.status_code != 200:
                return {'succ': False, 'data':"{'msg': 'detail status_code not 200'}"}
        except Exception as er:
            logger.error(er, exc_info=1)
            return {'succ': False}
        res = res.content.decode('utf-8')
        res = json.loads(res)
        channels = res.get('data').get('kill') if res.get('data') else []
        logger.info('get_data|succ')
        data = res.get('data')
        if not data:
            data = {'msg': 'no data', 'product_name': self.platform}
        data['product_name'] = self.platform
        return {'succ': True, 'data': [data, channels]}
        
    def login_and_get_data(self, ui):
        # 获取时间
        mths, days = u.make_dates(ms=None, ys=None, ye=None, me=None)
        # 登陆
        login_res = self.runLogin()
        if not login_res['succ']:
            return login_res
        cookies = login_res.get('cookies')

        # 获取上个月到现在每天的数据
        channels = None
        data_list = []
        for start_date, end_date in days:
            res = self.get_data(cookies, start_date, end_date)
            if not res.get('succ'):
                return {'succ': False, 'msg': res.get('data')}
            if res.get('msg') == 'no data':
                continue
            data_list.append(1)
            channels = res.get('data')[1]
            file_name = os.path.join(self.dir_path, '%s_%s.json' % (start_date, end_date))
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(json.dumps(res['data'][0], ensure_ascii=False))
            logger.info('文件写入成功：%s' % file_name)
            time.sleep(0.25)

        # 是否有数据
        if len(data_list) == 0:
            return {'succ': True, 'msg': 'no data'}
        self.result_kwargs['has_data'] = 1

        self.d.get('http://tg.app.sogou.com/common.php?action=dataPerday')
        self.d.execute_script('document.querySelector("#main").setAttribute("style", "float:left")')
        for sd, ed in days:
            self.get_img(sd, ed, channels)
        self.d.quit()

        return {'succ': True}

