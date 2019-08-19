'''
cpa http://cp.chaohuida.com:9097/manage/user/login.html zly
'''
from platform_crawler.utils.utils import Util
import requests
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.spiders.pylib.task_process import TaskProcess
from platform_crawler import settings

import json
from selenium.webdriver.common.by import By
import time
import os
import re
from html.parser import HTMLParser

u = Util()
logger = None
gHost = 'http://cp.chaohuida.com:9097'


# 解析html文档
class hp(HTMLParser):
    a_text = False
    index = 0

    def __init__(self):
        self.urlArr = []
        self.resArr = []
        super(hp, self).__init__()

    def handle_starttag(self, tag, attr):
        if tag == 'a' and len(attr) == 4 and attr[2][0] == 'target' and attr[2][1] == 'conFrame':
            self.urlArr.append(attr[1][1])
            self.a_text = True

    def handle_endtag(self, tag):
        if tag == 'a':
            self.a_text = False

    def handle_data(self, data):
        if self.a_text:
            data = data.replace('\n', '')
            data = data.strip()
            self.resArr.append(data)


class hp1(HTMLParser):
    a_text = False
    index = 0

    def __init__(self):
        self.resArr = []
        super(hp1, self).__init__()

    def handle_starttag(self, tag, attr):
        if tag == 'tr' and len(attr) == 1 and attr[0][0] == 'id' and attr[0][1].startswith('list_tr'):
            self.a_text = True

    def handle_endtag(self, tag):
        if tag == 'tr':
            self.a_text = False

    def handle_data(self, data):
        if self.a_text:
            data = data.replace('\n', '')
            data = data.strip()
            if data == '':
                return
            self.resArr.append(data)


class hp2(HTMLParser):
    a_text = False
    total_page = None

    def __init__(self):
        self.resArr = []
        super(hp2, self).__init__()

    def handle_starttag(self, tag, attr):
        if tag == 'td' and len(attr) == 3 and attr[0][0] == 'align' and attr[0][1] == 'left' and attr[1][
            0] == 'width' and attr[1][1] == '30%' and attr[2][0] == 'class' and attr[2][1] == 'blue':
            self.a_text = True

    def handle_endtag(self, tag):
        if tag == 'tr':
            self.a_text = False

    def handle_data(self, data):
        if self.a_text:
            try:
                grps = re.search(r'第(\d)/(\d)页', data).groups()
                print(grps, len(grps))
                if len(grps) == 2 and self.total_page == None:
                    print('inner %s' % self.total_page)
                    self.total_page = grps[1]
            except Exception as e:
                pass


class XsdqSpider(TaskProcess):
    def __init__(self, user_info, **kwargs):
        global logger
        self.user_info = user_info
        super().__init__(is_cpa=True, user_info=user_info, **kwargs)
        logger = self.logger

    # pytesseract识别二维码
    def realizeCode(self, vcimgpath):
        with open(vcimgpath, 'rb') as f:
            img = f.read()
        vc = u.rc.rk_create(img, 2040)
        logger.info('realizeCode|识别结果：%s' % vc)
        vc_res = vc.get('Result').lower()
        return vc_res, vc, img

    def login(self, ui):
        self.d.get(ui.get('loginUrl'))
        time.sleep(1)
        inpAccount = self.wait_element(By.CSS_SELECTOR, 'input#user_name')
        inpAccount.clear()
        inpAccount.send_keys(ui['account'])
        time.sleep(1)
        inpPassword = self.d.find_element_by_id('pass_word')
        inpPassword.clear()
        inpPassword.send_keys(ui['password'])
        time.sleep(1)

        vcimgpath = settings.join(settings.IMG_PATH, 'app_imgs', 'xsdqVerifyCode.png')
        vcodeimg = self.d.find_element_by_id('captcha_img')
        u.cutimg_by_driver(self.d, vcodeimg, vcimgpath)
        lk, lk_obj, im = self.realizeCode(vcimgpath)
        if lk == None or len(lk) == 0:
            logger.error('识别错误')
            return False
        inpVcode = self.d.find_element_by_id('security_code')
        inpVcode.send_keys(lk)
        time.sleep(3)

        sub_btn = self.wait_element(By.CSS_SELECTOR, 'input#sub_btn')
        sub_btn.click()
        time.sleep(3)

        try:
            mainFrame = self.wait_element(By.CSS_SELECTOR, 'frame#mainFrame')
            logger.info('login|succ')
            u.rc.rk_report(im, 3040, lk, vc_type=ui.get('platform'))
            return {'succ': True, 'cookies': self.d.get_cookies()}
        except Exception as e:
            try:
                text = self.d.find_element_by_id('err_msg').text
                if text == '验证码不对':
                    u.rc.rk_report_error(lk_obj.get('Id'))
                    logger.info('login|step1 error:验证码错误')
            finally:
                return False

    # 登录重试
    def runLogin(self, ui):
        for e in range(1, 6):
            self.init_browser()
            res = self.login(ui)
            if not res:
                self.d.quit()
            else:
                return res
        else:
            # params = [self.user_info.get('id'), self.user_info.get('account'), self.user_info.get('platform'), None,
            #           False]
            # if not post_res(*params):
            #     logger.error('----------useless account! Post result failed!')
            # else:
            logger.info('useless account!(%s) Post success!' % self.user_info)

            self.d.quit()
            return {'succ': False, 'invalid_account': True}

    # 获取submenu
    def get_submenus(self, cookie):
        ckstr = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in cookie])
        url = '%s/manage/left5.htm' % gHost
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
            'Cookie': ckstr
        }
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            logger.error('get_submenus|status code %s' % res.status_code)
            return False
        res = res.content.decode('utf-8')

        yk = hp()
        yk.feed(res)
        yk.close()

        if len(yk.resArr) <= 0:
            logger.error('get_submenus|error no data %s' % yk.resArr)
            return False

        res = []
        for urlidx, url in enumerate(yk.urlArr):
            tmp = {}
            tmp['name'] = yk.resArr[urlidx]
            tmp['url'] = url
            res.append(tmp)
        logger.info('get_submenus|result: %s' % res)
        return res

    def get_data_bymenu(self, submenu, cookie, osd, oed):
        pageidx = 1
        totalpage = -1
        alldata = []

        while totalpage == -1 or pageidx <= totalpage:
            url = '%s%s?channelNo=&beginTime=%s&endTime=%s&page=%s' % (gHost, submenu.get('url'), osd, oed, pageidx)
            ckstr = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in cookie])
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
                'Cookie': ckstr
            }
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code != 200:
                logger.error('get_data_bymenu|status code %s' % res.status_code)
                return False

            yk = hp2()
            yk.feed(res.text)
            yk.close()
            logger.info('hp2 totalpage: %s' % yk.total_page)
            # 赋值总页数
            totalpage = int(yk.total_page)

            if not yk.total_page:
                logger.error('get_data_bymenu|totalpage error %s' % yk.total_page)
                return False
            logger.info('get_data_bymenu|当前页：%s  总页数：%s' % (pageidx, yk.total_page))

            yk = hp1()
            yk.feed(res.text)
            yk.close()
            logger.info('hp1 data: %s' % yk.resArr)

            if not yk.resArr:
                logger.error('get_data_bymenu|resArr error %s' % yk.resArr)
                return False
            logger.info('get_data_bymenu|该页数据：%s' % yk.resArr)

            for idx, td in enumerate(yk.resArr):
                if idx % 3 == 0:
                    tmp = {}
                    tmp['date'] = td
                elif idx % 3 == 1:
                    tmp['channel'] = td
                elif idx % 3 == 2:
                    tmp['actuser'] = td
                    alldata.append(tmp)
                    logger.info('get_data_bymenu|alldata append:%s' % tmp)

            # index自增
            pageidx = pageidx + 1
            time.sleep(0.5)

        return alldata

    # 按查询管理子菜单分文件
    def get_data(self, cookie, osd, oed):
        data_list = []
        submenus = self.get_submenus(cookie)
        for submenu in submenus:
            alldata = self.get_data_bymenu(submenu, cookie, osd, oed)
            if not alldata:
                continue
            data_list.append(1)
            filepath = os.path.join(self.dir_path, '%s_%s_%s.json' % (osd, oed, submenu.get('name')))
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json.dumps(alldata, ensure_ascii=False))
            logger.info('get_data|文件写入成功%s' % filepath)
        if not data_list:
            return False
        return True

    def ele_click(self, element):
        element.click()
        self.d.implicitly_wait(10)

    def switch_frame(self, targ):
        self.d.switch_to.default_content()
        self.d.switch_to.frame('mainFrame')
        self.d.switch_to.frame('centerFrame')
        self.d.switch_to.frame(targ)

    def change_date(self, sd, ed):
        self.d.execute_script('document.querySelector("#beginTime").value="%s"' % sd)
        self.d.execute_script('document.querySelector("#endTime").value="%s"' % ed)
        self.d.execute_script('document.querySelector("#search_btn").click()')
        self.d.implicitly_wait(10)

    def get_img(self, sd, ed):
        self.switch_frame('conFrame')
        self.change_date(sd, ed)
        pic_name = '%s_%s' % (sd, ed)
        self.d.switch_to.default_content()
        height = self.d.execute_script('return document.querySelector("frameset").offsetHeight')
        if height < 964:
            height = None
        cut_res = cut_img(height, self.dir_path, pic_name)
        if not cut_res.get('succ'):
            logger.error('cut picture failed, possible msg:\ndir_path:%s\npic_name: %s' % (self.dir_path, pic_name))
        logger.info('got a picture: pic_msg: %s' % os.path.join(self.dir_path, pic_name))
        self.switch_frame('I1')

    def get_img_process(self, sd, ed):
        self.d.switch_to.frame('topFrame')
        # top_height = self.d.execute_script('return document.documentElement.offsetHeight')
        self.switch_frame('I1')
        menu_list = self.d.find_elements_by_xpath('//a[@name="item"]')
        for menu in menu_list:
            self.ele_click(menu)
            self.get_img(sd, ed)
        self.d.switch_to.default_content()

    def has_data_or_pic(self):
        # 是否有数据
        def functool(z):
            if 'json' in z:
                return 0
            if 'png' in z or 'jpg' in z:
                return 1
        files = [functool(x) for x in os.listdir(self.dir_path)]
        if 0 not in files:
            self.result_kwargs['has_data'] = 0
        if 1 not in files:
            self.result_kwargs['has_pic'] = 0

    def login_and_get_data(self, ui):
        # 获取时间
        mths, days = u.make_dates(ms=None, ys=None, ye=None, me=None)

        # 登陆
        login_res = self.runLogin(ui)
        if not login_res['succ']:
            return login_res
        cookies = login_res.get('cookies')

        # 获取上个月到现在每天的数据
        data_list = []
        for start_date, end_date in days:
            try:
                res = self.get_data(cookies, start_date, end_date)
                if not res:
                    logger.error('get_data|error')
                    continue
                data_list.append(1)
            except Exception as e:
                logger.error(e)

        if not data_list:
            return {'succ': True, 'msg': 'no data'}

        for sd, ed in days:
            self.get_img_process(sd, ed)

        return {'succ': True}

