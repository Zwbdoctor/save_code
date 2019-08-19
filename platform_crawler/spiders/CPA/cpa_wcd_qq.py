'''
cpa http://unicorn.wcd.qq.com/login.html zly
'''
import json
import math
import time
import os
import re

from selenium.webdriver.common.by import By
from PIL import Image
import pytesseract
import requests

from platform_crawler.utils.utils import Util
from platform_crawler.utils.post_get import get
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.spiders.pylib.task_process import TaskProcess, EC
from platform_crawler import settings

u = Util()
logger = None


class WcdQQSpider(TaskProcess):
    def __init__(self, user_info, **kwargs):
        global logger
        self.user_info = user_info
        super().__init__(is_cpa=True, user_info=user_info, **kwargs)
        self.cookies = None
        logger = self.logger

    def clickToLogin(self):
        self.d.get('https://unicorn.wcd.qq.com/login.html')
        self.wait_element(By.ID, 'username')
        # headerLoginBtn.click()
        loginIfr = self.wait_element(By.CSS_SELECTOR, 'iframe[id="ui.ptlogin"]')
        return loginIfr

    # 检验是否登录成功，cookie存储的只是sessionId
    def isLogin(self):
        url = 'https://unicorn.wcd.qq.com/mainframe.html'
        cookie = self.d.get_cookies()
        cookie = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in cookie])
        header = {
            'Cookie': cookie,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
        }
        testres = requests.get(url, headers=header, allow_redirects=False)
        logger.info('isLogin requests.head status_code:%d, headerslocation:%s' % (
        testres.status_code, testres.headers.get('location')))
        if testres.status_code == 302 and re.search(r"login.html", testres.headers.get('location')):
            return False
        elif testres.status_code == 200:
            return True

    # pytesseract识别二维码
    def realizeCode(self, vcimgpath):
        img = Image.open(vcimgpath)
        img = img.convert('RGBA')
        pix = img.load()

        # 去周围黑框
        for x in range(img.size[0]):
            pix[x, 0] = pix[x, img.size[1] - 1] = (255, 255, 255, 255)
        for y in range(img.size[1]):
            pix[0, y] = pix[img.size[0] - 1, y] = (255, 255, 255, 255)

        # 二值化
        for x in range(img.size[0]):
            for y in range(img.size[1]):
                if pix[x, y][0] < 60 and pix[x, y][1] < 60 and pix[x, y][2] < 60:
                    pix[x, y] = (0, 0, 0, 255)
                else:
                    pix[x, y] = (255, 255, 255, 255)

        img.save(vcimgpath)
        resvc = pytesseract.image_to_string(vcimgpath)
        resvc = resvc.replace(' ', '')  # 去空格
        logger.info('pytesseract识别结果：%s', resvc)
        return resvc

    def login(self, ui):
        self.d.get('https://unicorn.wcd.qq.com/login.html')
        time.sleep(1)
        inpUsername = self.wait_element(By.ID, 'username')
        inpUsername.clear()
        inpUsername.send_keys(ui['account'])
        inpPassword = self.d.find_element_by_id('password')
        inpPassword.clear()
        inpPassword.send_keys(ui['password'])
        time.sleep(1)
        vcimgpath = settings.join(settings.IMG_PATH, 'app_imgs', 'wcdVerifyCode.png')
        vcodeimg = self.d.find_element_by_id('v-code-img')
        u.cutimg_by_driver(self.d, vcodeimg, vcimgpath)
        # im = None
        # with open(vcimgpath, 'rb') as f:
        #     im = f.read()
        # lk = u.rc.rk_create(im, '3040').get('Result')
        lk = self.realizeCode(vcimgpath)

        inpVcode = self.d.find_element_by_id('v-code')
        inpVcode.send_keys(lk)
        btnLogin = self.d.find_element_by_css_selector('.btn-login')
        btnLogin.click()
        time.sleep(4)

        loginRes = self.isLogin()
        logger.info('isLogin:%s' % loginRes)
        if self.isLogin():
            return {'succ': True, 'cookies': self.d.get_cookies()}
        else:
            return {'succ': False, 'msg': 'login fail'}

    # 登录重试
    def runLogin(self, ui):
        for e in range(1, 6):
            self.init_browser()
            res = self.login(ui)
            if res['succ']:
                return res
            else:
                self.d.quit()
        else:
            # params = [self.user_info.get('id'), self.user_info.get('account'), self.user_info.get('platform'), None,
            #           False]
            # if not post_res(*params):
            #     logger.error('----------useless account! Post result failed!')
            # else:
            logger.info('useless account!(%s) Post success!' % self.user_info)

            self.d.quit()
            return {'succ': False, 'invalid_account': True}

    def get_product_detail(self, productRes, vendorRes, headers, osd, oed):
        # 请求4
        for item in productRes:
            curPage = 1
            total = -1
            pageSize = 100
            alldata = []
            productId = item.get('key')

            logger.info('开始产品：%s' % item.get('value'))
            while total == -1 or curPage <= math.ceil(total / pageSize):
                url = 'https://unicorn.wcd.qq.com/free/getPayDataTable.html'
                params = {
                    'timeArea': osd.replace('-', '') + ' - ' + oed.replace('-', ''),
                    'product': productId,
                    'platform': 'android,iphone,ipad,apad,windows',
                    'vendor': ','.join(vendorRes),
                    # 'channel': ','.join(channelRes),
                    'channel': None,
                    'datatype': 'd',
                    'dataValue': 'newUser',
                    'fee': '1,0',
                    'fileType': '',
                    'pageSize': pageSize,
                    'curPage': curPage
                }
                logger.info('product:%s,  curPage:%d, total:%d' % (item.get('value'), curPage, total))
                dataRes = get(url, params=params, headers=headers)
                if not dataRes.get('is_success'):
                    logger.error('product:%s,  curPage:%d, total:%d, got failed' % (item.get('value'), curPage, total))
                    curPage += 1
                    continue
                dataRes = dataRes.get('msg').json()
                alldata = alldata + dataRes.get('data')
                total = dataRes['total']
                curPage += 1

            if not alldata:
                continue
            product_file_name = os.path.join(self.dir_path, '%s_%s_%s.json' % (osd, oed, item.get('value')))
            with open(product_file_name, 'w', encoding='utf-8') as f:
                f.write(json.dumps(alldata, ensure_ascii=False))

    # 数据较多，按产品分文件
    def get_data(self, osd, oed):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Cookie': self.cookies,
            'Host': 'unicorn.wcd.qq.com',
            'Referer': 'https://unicorn.wcd.qq.com/paydata/paydatafree.html',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
        }

        # 请求1
        productUrl = 'https://unicorn.wcd.qq.com/mcare/product.html'
        productRes = get(productUrl, headers=headers, timeout=120)
        if not productRes.get('is_success'):
            return {'succ': False, 'data': "{'msg': 'request time out'}"}
        productResJson = productRes.get('msg').json()
        productRes = [x for x in productResJson.get('data') if int(x.get('key')) > 0]

        # 请求2
        vendorUrl = 'https://unicorn.wcd.qq.com/mcare/vendor.html'
        vendorRes = get(vendorUrl, headers=headers, timeout=120)
        if not vendorRes.get('is_success'):
            return {'succ': False, 'data': "{'msg': 'request time out'}"}
        vendorResJson = vendorRes.get('msg').json()
        vendorRes = [x.get('key') for x in vendorResJson.get('data') if int(x.get('key')) > 0]

        # 请求3
        channelUrl = "https://unicorn.wcd.qq.com/mcare/channel.html"
        channelRes = get(channelUrl, headers=headers)
        if not channelRes.get('is_success'):
            return {'succ': False, 'data': "{'msg': 'request time out'}"}
        channelResStr = channelRes.get('msg').json()
        # channelRes = [x for x in channelResStr.get('data') if int(x.get('key')) > 0]

        # 请求4
        self.get_product_detail(productRes, vendorRes, headers, osd, oed)

        return {'succ': True,
                'msg': {'channelList': channelResStr, 'productList': productResJson, 'vendorList': vendorResJson}}

    def has_data(self, sd, ed, productId, vendor, channel):
        cookie = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in self.d.get_cookies()])
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Cookie': cookie,
            'Host': 'unicorn.wcd.qq.com',
            'Referer': 'https://unicorn.wcd.qq.com/paydata/paydatafree.html',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
        }
        url = 'https://unicorn.wcd.qq.com/free/getPayDataTable.html'
        params = {
            'timeArea': '%s - %s' % (sd, ed), 'product': ','.join(productId),
            'platform': 'android,iphone,ipad,apad,windows', 'vendor': ','.join(vendor),
            'channel': channel,
            'datatype': 'd', 'dataValue': 'newUser', 'fee': '1,0', 'fileType': '', 'pageSize': 50, 'curPage': 1
        }
        dataRes = get(url, params=params, headers=headers)
        if not dataRes.get('is_success'):
            return False
        dataRes = dataRes.get('msg').json()
        time.sleep(0.2)
        if dataRes.get('total') == 0:
            return False
        return dataRes.get('total')

    def get_img(self, sd, ed, data):
        pids = [x.get('key') for x in data.get('productList').get('data') if int(x.get('key')) > 0]
        venders = [x.get('key') for x in data.get('vendorList').get('data') if int(x.get('key')) > 0]
        sd, ed = sd.replace('-', ''), ed.replace('-', '')
        self.wait_element(By.ID, 'ifm1', ec=EC.frame_to_be_available_and_switch_to_it)
        self.wait_element(By.CSS_SELECTOR, 'a.tabs-close').click()
        self.wait_element(By.ID, 'filetree_1_span').click()  # 点击数据统计
        self.wait_element(By.ID, 'filetree_3_span').click()  # 点击 CPA合作（含免费）
        time.sleep(1)
        self.d.switch_to.frame('ifm2')
        date_input = self.wait_element(By.ID, 'reservation', ec=EC.presence_of_element_located)
        date_input.clear()
        date_input.send_keys("%s - %s" % (sd, ed))
        self.wait_element(By.CLASS_NAME, 'applyBtn').click()
        for item in data.get('channelList').get('data'):  # 循环所有渠道，截图
            if int(item.get('key')) < 0:
                logger.info('item key < 0, pass')
                continue
            res = self.has_data(sd, ed, pids, venders, item.get('key'))
            time.sleep(0.2)
            if not res:
                logger.info(f'cut_img | data_range| {sd} ~ {ed} | {item.get("value")}')
                continue
            self.d.execute_script('document.querySelector("#channelSelect").value="%s"' % (item.get('key')))
            self.d.execute_script(
                'document.querySelector(".searchbox div:nth-child(5) span:nth-child(2)").textContent="%s"' % (
                    item.get('value')))
            self.d.execute_script('document.querySelector("#feeSelect").value="1,0"')
            self.d.execute_script('document.querySelector(".searchbox div:nth-child(6) span:nth-child(2)").textContent="是否付费(2条)"')
            self.wait_element(By.XPATH, '//*[@class="searchbox"]//div[5]//span[2]')
            time.sleep(1)
            self.wait_element(By.ID, 'searchBtn')
            self.wait_element(By.ID, 'searchBtn', ec=EC.element_to_be_clickable).click()
            self.d.execute_script('document.querySelector("#ui-multiselect-5-option-2").click()')  # 设置显示条数
            # self.d.execute_script(
            #     "document.querySelector('.page_size_box button span:nth-child(2)').textContent='每页显示50行'"
            # )
            time.sleep(0.5)
            pgs = res // 50 if res > 50 else 1
            for p in range(pgs):
                pic_name = "%s_#%s_#%s_#page%s.png" % (item.get('value'), sd, ed, p + 1)
                height = self.d.execute_script('return document.body.offsetHeight')
                cut_res = cut_img(height, self.dir_path, pic_name)
                if not cut_res['succ']:
                    logger.error(
                        'cut picture failed, possible msg:\ndir_path:%s\npic_name: %s' % (self.dir_path, pic_name))
                logger.info('got a picture: pic_msg: %s' % os.path.join(self.dir_path, pic_name))
                if pgs > 1:
                    self.wait_element(By.CLASS_NAME, 'pageDown').click()
                self.d.switch_to.default_content()
                self.d.execute_script("document.documentElement.scrollTop=0")
                self.d.switch_to.frame('ifm1')
                self.d.switch_to.frame('ifm2')
                time.sleep(0.3)
        else:
            self.d.switch_to.default_content()

    def has_data_or_pic(self):
        # 是否有数据
        def functool(z):
            if 'json' in z:
                return 0
            if 'png' in z:
                return 1
        files = [functool(x) for x in os.listdir(self.dir_path)]
        if 0 not in files:
            self.result_kwargs['has_data'] = 0
        if 1 not in files:
            self.result_kwargs['has_pic'] = 0

    def login_part(self, ui, **kwargs):
        # 登陆
        return self.runLogin(ui)

    def deal_login_result(self, login_res):
        if not login_res['succ']:
            return login_res
        self.cookies = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in login_res.get('cookies')])

    def get_data_part(self, ui, **kwargs):
        # 获取时间
        self.get_dates = 2      # 包含本月前的2个自然月
        days = self.get_dates
        # 获取上个月到现在每天的数据
        data_list = []
        for start_date, end_date in days:
            try:
                res = self.get_data(start_date, end_date)
                if res.get('succ'):
                    data_list.append([start_date, end_date, res.get('msg')])
            except Exception as e:
                logger.error(e, exc_info=1)
        logger.info('got data complete | start to upload data')
        # 上传数据 ###########################
        self.upload_file()
        self.remove_json_files()
        return data_list

    def remove_json_files(self):
        files = os.listdir(self.dir_path)
        for f in files:
            if f.endswith('json'):
                os.remove(os.path.join(self.dir_path, f))

    def get_img_part(self, get_data_res=None, **kwargs):
        # 根据爬取的数据信息，进行截图
        for sd, ed, data in get_data_res:
            # try:
            self.get_img(sd, ed, data)
            # except Exception as e:
            #     logger.error(e, exc_info=1)
            #     self.d.switch_to.default_content()
            #     continue
        else:
            self.d.quit()

        return {'succ': True}

