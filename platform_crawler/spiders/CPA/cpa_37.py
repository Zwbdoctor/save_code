'''
cpa http://union.m.37.com/user/login zly
'''
from platform_crawler.utils.utils import Util
import requests
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.spiders.pylib.task_process import TaskProcess
from platform_crawler.settings import join, IMG_PATH

import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from html.parser import HTMLParser

u = Util()
logger = None


# 解析html文档
class hp(HTMLParser):
    a_text = False
    index = 0

    def __init__(self):
        self.resArr = []
        super(hp, self).__init__()

    def handle_starttag(self, tag, attr):
        if tag == 'td':
            self.a_text = True

    def handle_endtag(self, tag):
        if tag == 'td':
            self.a_text = False

    def handle_data(self, data):
        if self.a_text:
            data = data.replace('\n', '')
            data = data.strip()
            if data == '':
                return
            self.resArr.append(data)


class Cpa37Spider(TaskProcess):
    def __init__(self, user_info, **kwargs):
        global logger
        super().__init__(is_cpa=True, user_info=user_info, **kwargs)
        logger = self.logger

    # pytesseract识别二维码
    def realizeCode(self, vcimgpath):
        with open(vcimgpath, 'rb') as f:
            img = f.read()
        vc = u.rc.rk_create(img, 3040)
        logger.info('realizeCode|识别结果：%s' % vc)
        vc_res = vc.get('Result').lower()
        return vc_res, vc, img

    def login(self, ui):
        self.d.get(ui.get('loginUrl'))
        time.sleep(1)
        inpAccount = self.wait_element(By.CSS_SELECTOR, 'input[name="ACCOUNT"]')
        inpAccount.clear()
        inpAccount.send_keys(ui['account'])
        time.sleep(1)
        inpPassword = self.d.find_element_by_css_selector('input[name="PASSWORD"]')
        inpPassword.clear()
        inpPassword.send_keys(ui['password'])
        time.sleep(1)

        vcimgpath = join(IMG_PATH, 'app_imgs', 'cpa37VerifyCode.png')
        vcodeimg = self.d.find_element_by_id('scode')
        u.cutimg_by_driver(self.d, vcodeimg, vcimgpath)
        lk, vc_obj, im = self.realizeCode(vcimgpath)
        if lk == None or len(lk) == 0:
            logger.error('识别错误')
            return False
        inpVcode = self.d.find_element_by_css_selector('input[name="CODE"]')
        inpVcode.send_keys(lk)
        time.sleep(3)

        # time.sleep(5)

        sub_btn = self.wait_element(By.CSS_SELECTOR, 'button[type="submit"]')
        sub_btn.click()
        time.sleep(3)

        try:
            alogout = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="/user/logout"]')))
            logger.info('login|succ')
            u.rc.rk_report(im, 3040, lk, vc_type=ui.get('platform'))
            return {'succ': True, 'cookies': self.d.get_cookies()}
        except Exception as e:
            try:
                alert = self.d.switch_to.alert()
                if '验证码错误' in alert.text:
                    logger.info('login|step1 error:验证码错误')
                    u.rc.rk_report_error(vc_obj.get('Id'))
            finally:
                logger.info('login|step1 error:验证码错误')
                return False

    # 登录重试
    def runLogin(self, ui):
        res = None
        for e in range(1, 6):
            self.init_browser()
            res = self.login(ui)
            if not res:
                self.d.quit()
            else:
                return res
        else:
            # params = [ui.get('id'), ui.get('account'), ui.get('platform'), None,
            #           False]
            # if not post_res(*params):
            #     logger.error('----------useless account! Post result failed!')
            # else:
            logger.info('useless account!(%s) Post success!' % ui)

            self.d.quit()
            return {'succ': False, 'invalid_account': True}

    # 按查询管理子菜单分文件
    def get_data(self, cookie, osd, oed):
        ckstr = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in cookie])
        url = 'http://union.m.37.com/union_data/channel_data/?sDate=%s&eDate=%s&gid=&cid=&selectAct=%s&SELECT=%s' % (
        osd, oed, 1, '查询')
        headers = {
            'Cookie': ckstr,
            'Referer': 'http://union.m.37.com/union_data/channel_data/?sDate=2018-09-01&eDate=2018-09-30&gid=&cid=&selectAct=1&SELECT=%E6%9F%A5%E8%AF%A2'
        }

        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            logger.error('get_data|status code is %s' % res.status_code)
            return False
        res = res.content.decode('utf-8')

        yk = hp()
        yk.feed(res)
        yk.close()

        alldata = []
        tmp = {}
        for idx, td in enumerate(yk.resArr):
            if idx % 6 == 0:
                tmp['date'] = td
            elif idx % 6 == 1:
                tmp['game'] = td
            elif idx % 6 == 2:
                tmp['channel'] = td
            elif idx % 6 == 3:
                tmp['channelNo'] = td
            elif idx % 6 == 4:
                tmp['registerNum'] = td
            elif idx % 6 == 5:
                tmp['rechargeMoney'] = td
                logger.info('get_data|行数据：%s' % tmp)
                alldata.append(tmp)
                tmp = {}

        filepath = os.path.join(self.dir_path, '%s_%s.json' % (osd, oed))
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json.dumps(alldata, ensure_ascii=False))
        logger.info('get_data|文件写入成功%s' % filepath)
        return True

    def get_img(self, sd, ed):
        url = 'http://union.m.37.com/union_data/channel_data/'
        self.d.get(url)
        self.d.execute_script('''document.querySelector("input[name='sDate']").value="%s"''' % sd)
        self.d.execute_script('''document.querySelector("input[name='eDate']").value="%s"''' % ed)
        self.d.execute_script('document.querySelector(".btn.green").click()')
        pic_name = '%s_%s.png' % (sd, ed)
        height = self.d.execute_script(r'return document.body.offsetHeight')
        cut_res = cut_img(height, self.dir_path, pic_name)
        if not cut_res['succ']:
            logger.error('cut picture failed, possible msg:\ndir_path:%s\npic_name: %s' % (self.dir_path, pic_name))
        logger.info('got a picture: pic_msg: %s' % os.path.join(self.dir_path, pic_name))
        return cut_res

    def login_and_get_data(self, ui):
        # 获取时间
        mths, days = u.make_dates(ms=None, ys=None, ye=None, me=None)

        # 登陆
        login_res = self.runLogin(ui)
        if not login_res['succ']:
            return login_res
        cookies = login_res.get('cookies')

        # 获取上个月到现在每天的数据
        for start_date, end_date in days:
            try:
                res = self.get_data(cookies, start_date, end_date)
                if not res:
                    logger.error('get_data|error')
                    return
            except Exception as e:
                logger.error(e, exc_info=1)

        try:
            for sd, ed in days:
                self.get_img(sd, ed)
        except Exception as ei:
            logger.error(ei, exc_info=1)
        finally:
            self.d.quit()

        return {'succ': True}
