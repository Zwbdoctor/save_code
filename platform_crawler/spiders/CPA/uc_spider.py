"""
cpa uc 财务爬虫 ---- http://union.uc.cn
"""
# from re import search
# import logging
from json import dump
import os
import time

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from pytesseract.pytesseract import image_to_string
from lxml.html import etree

from platform_crawler.spiders.pylib.task_process import TaskProcess
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.utils.utils import Util
from platform_crawler.settings import IMG_PATH, join


logger = None
base_header = {
    'accept': "application/json, text/javascript, */*; q=0.01",
    'cookie': None,
    'Referer': "https://e.qq.com/atlas/5713092/account/list",
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3569.0 Safari/537.36",
}


class LoginUC:

    def __init__(self, ui):
        self.d = None
        self.wait = None
        self.user_info = ui
        self.acc, self.pwd = ui.get('account'), ui.get('password')
        self.datapass = ui.get('dataPassword')

    def init_browser(self):
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.support.wait import WebDriverWait
        co = Options()
        co.add_argument('--headless')
        self.d = webdriver.Chrome(options=co)
        self.d.delete_all_cookies()
        self.d.set_page_load_timeout(60)
        self.d.set_script_timeout(60)
        self.d.maximize_window()
        self.wait = WebDriverWait(self.d, 20)

    def waitElement(self, element_type, wait_sth):
        ele = self.wait.until(EC.visibility_of_element_located((element_type, wait_sth)))
        return ele

    def ch_img(self, img_path):
        from PIL import Image
        im = Image.open(img_path)
        # 转化到灰度图
        imgry = im.convert('L')
        # 保存图像
        imgry.save(img_path)
        # 二值化，采用阈值分割法，threshold为分割点
        threshold = 135
        table = []
        for j in range(256):
            if j < threshold:
                table.append(0)
            else:
                table.append(1)
        out = imgry.point(table, '1')
        out.save(img_path)
        # 识别
        text = image_to_string(out, lang='eng')
        text = text.replace(' ', '').replace('.', '').lower()
        return text

    def deal_vc(self):
        ele = self.wait.until(EC.visibility_of_element_located((By.ID, 'checkpic')))
        img_path = join(IMG_PATH, 'vc.png')
        Util().cutimg_by_driver(self.d, ele, img_path)
        # with open(img_path, 'br') as i:
        #     im = i.read()
        vc = self.ch_img(img_path)
        if not vc:
            ele.click()
            return self.deal_vc()
        return vc

    def is_login(self):
        time.sleep(3)
        try:
            self.d.find_element_by_name('Submit')
            msg = self.d.find_element_by_css_selector('td[valign="top"] td > div').text
            return {'succ': False, 'msg': msg}
        except:
            return {'succ': True}

    def run(self):
        for e in range(3):
            try:
                self.d.get('http://union.uc.cn/')
                break
            except:
                continue
        self.wait.until(EC.visibility_of_element_located((By.ID, 'account'))).clear()
        self.wait.until(EC.visibility_of_element_located((By.ID, 'account'))).send_keys(self.acc)
        self.wait.until(EC.visibility_of_element_located((By.ID, 'password'))).send_keys(self.pwd)
        vc = self.deal_vc()
        if not vc:
            return self.run()
        self.wait.until(EC.visibility_of_element_located((By.NAME, 'validate_code'))).send_keys(vc)
        self.wait.until(EC.visibility_of_element_located((By.NAME, 'Submit'))).click()
        msg = self.is_login()
        if not msg.get('succ') and msg.get('msg') == '验证码错误!':
            return self.run()
        elif not msg.get('succ') and msg.get('msg') == '帐号或密码不正确!':
            return {'succ': False}
        try:
            self.wait.until(EC.visibility_of_element_located((By.NAME, 'datapassword'))).send_keys(self.datapass)
        except:
            return {'succ': False}
        self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'but'))).click()
        time.sleep(2)
        cookie = self.d.get_cookies()
        return {'succ': True, 'cookie': cookie}

    def run_login(self):
        self.init_browser()
        res = None
        for i in range(5):
            try:
                res = self.run()
                if res.get('succ'):
                    res['driver'] = self.d
                    break
            except Exception as e:
                logger.error(e, exc_info=1)
                res = {'succ': False}
        if not res.get('succ'):
            # params = [self.user_info.get('id'), self.user_info.get('account'), self.user_info.get('platform'), None, False]
            # if not post_res(*params):
            #     logger.error('login failed, post failed')
            logger.info('login failed, post success')
            res['invalid_account'] = True
        # self.d.quit()
        return res


class UCSpider(TaskProcess):

    def __init__(self, user_info, **kwargs):
        global logger
        self.cookies = {}
        super().__init__(user_info=user_info, **kwargs)
        logger = self.logger

    def xpath(self, element, text):
        ele = element.xpath(text)
        return ele[0] if isinstance(ele, list) and len(ele) > 0 else ''

    def get_products_info(self):
        url = "http://union.uc.cn/account_manage/mycount.php"
        # payload = "action=datapass&datapassword=%s" % data_password
        headers = {
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            # 'Content-Type': "application/x-www-form-urlencoded",
            'Cookie': self.cookies,
            'Host': "union.uc.cn",
            'Referer': "http://union.uc.cn/account_manage/datapassword.php",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3569.0 Safari/537.36",
        }
        res = self.deal_result(self.execute('GET', url, headers=headers, verify=False))
        if not res.get('succ'):
            return res
        html = etree.HTML(res.get('msg'))
        zd = self.xpath(html, '//*[@id="zd"]/option/@value')
        zd_name = html.xpath('//*[@id="zd"]/option/text()')[0]

        pids = html.xpath('//*[@id="cp"]/option')
        p_list = []
        for p in pids:
            pv = p.xpath('./@value')[0]
            pn = p.xpath('./text()')[0]
            if '所有产品' in pn:
                continue
            p_list.append({'name': pn, 'value': pv})
        return {'name': zd_name, 'value': zd}, p_list

    def get_data_process(self, sd, ed):
        file_name = '%s_%s.json' % (sd, ed)
        zds, pids = self.get_products_info()
        data = None
        for p in pids:
            res = self.get_data(sd, ed, zds, p, data=data)
            if not res.get('succ'):
                return res
            data = res.get('msg')
        else:
            with open(os.path.join(self.dir_path, file_name), 'w', encoding='utf-8') as f:
                dump(data, f)
        return {'succ': True, 'pids': pids}

    def get_data(self, sd, ed, sid, pid, data=None):
        url = "http://union.uc.cn/account_manage/mycount.php?sid=%(sid)s&pid=%(pid)s&sdate=%(sd)s&edate=%(ed)s" % {
            'sid': sid.get('value'), 'pid': pid.get('value'), 'sd': sd, 'ed': ed
        }
        res = self.deal_result(self.execute('GET', url, set_cookies=True))
        if not res.get('succ'):
            return res
        html = etree.HTML(res.get('msg'))
        trs = html.xpath('//div[@class="account-c"]/table//tr')[1:]
        data = {'datas': []} if not isinstance(data, dict) else data
        d = {'name': sid.get('name'), 'data': []}
        for tr in trs:
            date = self.xpath(tr, './td[1]/text()')
            num = self.xpath(tr, './td[2]/a/text()')
            d.get('data').append({'date': date, 'install_num': num})
        data.get('datas').append(d)
        return {'succ': True, 'msg': data}

    def change_date(self, sd, ed):
        self.wait_element(By.ID, 'sdate').clear()
        self.wait_element(By.ID, 'sdate').send_keys(sd)
        self.wait_element(By.ID, 'edate').clear()
        self.wait_element(By.ID, 'edate').send_keys(ed)
        self.wait_element(By.CLASS_NAME, 'but').click()

    def get_img(self, sd, ed, pid):
        s = Select(self.wait_element(By.ID, 'cp'))
        s.select_by_value(pid.get('value'))
        self.wait_element(By.CLASS_NAME, 'but').click()
        time.sleep(0.5)
        pic_name = '%s_%s_%s.png' % (pid.get('name'), sd, ed)
        cut_res = cut_img(None, self.dir_path, pic_name)
        if not cut_res.get('succ'):
            logger.error(cut_res)

    def login_and_get_data(self, ui):
        # login
        lu = LoginUC(ui).run_login()
        if not lu.get('succ'):
            return lu
        self.d = lu.pop('driver')
        self.wait = WebDriverWait(self.d, 20)
        self.cookies = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in lu.get('cookie')])

        # 获取数据
        data = []
        mths, dates = Util().make_dates(ys=None, ms=None, ye=None, me=None)
        for sd, ed in dates:
            res = self.get_data_process(sd, ed)
            if not res.get('succ'):
                return res
            data.append([sd, ed, res.get('pids')])

        # 截图
        try:
            for sd, ed, pids in data:
                self.change_date(sd, ed)
                for pid in pids:
                    self.get_img(sd, ed, pid)
        finally:
            self.d.quit()

        return {'succ': True}
