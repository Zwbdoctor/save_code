'''
cpa http://xkwlm.koowo.com/admin/login zly
    update v2 >>> add model:  cut_img        --- zwb
'''
from platform_crawler.utils.utils import Util
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.spiders.pylib.task_process import TaskProcess
from platform_crawler.settings import IMG_PATH, join

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import json
import requests
import time
import os
from html.parser import HTMLParser

u = Util()
logger = None
gHost = 'http://cp.chaohuida.com:9097'
log_name = __name__.split('.')[-1]


class hp(HTMLParser):
    a_text = False
    index = 0

    def __init__(self):
        self.resArr = []
        super(hp, self).__init__()

    def handle_starttag(self, tag, attr):
        if tag == 'option' and len(attr) == 1 and attr[0][0] == 'value' and attr[0][1].startswith('kwplayer_'):
            self.a_text = True

    def handle_endtag(self, tag):
        if tag == 'option':
            self.a_text = False

    def handle_data(self, data):
        if self.a_text:
            data = data.replace('\n', '')
            data = data.strip()
            if data == '':
                return
            self.resArr.append(data)


class hp1(HTMLParser):
    a_text = False
    index = 0

    def __init__(self):
        self.resArr = []
        super(hp1, self).__init__()

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


class KwyySpider(TaskProcess):
    def __init__(self, user_info, **kwargs):
        global logger
        super().__init__(is_cpa=True, user_info=user_info, **kwargs)
        logger = self.logger

    # pytesseract识别二维码
    def realizeCode(self, vcimgpath):
        with open(vcimgpath, 'rb') as f:
            img = f.read()
        vc_obj = u.rc.rk_create(img, 3040)
        vc = vc_obj.get('Result').lower()
        logger.info('realizeCode|识别结果：%s' % vc_obj)
        return vc, vc_obj, img

    def login(self, ui):
        self.d.get(ui.get('loginUrl'))
        time.sleep(1)
        inpAccount = self.wait_element(By.CSS_SELECTOR, 'input#username')
        inpAccount.clear()
        inpAccount.send_keys(ui['account'])
        time.sleep(1)
        inpPassword = self.d.find_element_by_id('password')
        inpPassword.clear()
        inpPassword.send_keys(ui['password'])
        time.sleep(1)

        vcimgpath = join(IMG_PATH, 'app_imgs', 'kwyyVerifyCode.png')
        time.sleep(1)
        # vcodeimg = self.waitElement(By.ID, 'captcha_img')
        try:
            vcodeimg = self.d.find_element_by_id('captcha_img')
            u.cutimg_by_driver(self.d, vcodeimg, vcimgpath)
            lk, lk_obj, im = self.realizeCode(vcimgpath)
            if lk == None or len(lk) == 0:
                logger.error('识别错误')
                return False
            inpVcode = self.d.find_element_by_id('security_code')
            inpVcode.send_keys(lk)
            time.sleep(3)
        except:
            logger.info('there is no verify img')
        # time.sleep(5)

        sub_btn = self.wait_element(By.ID, 'sign-in-btn')
        sub_btn.click()
        time.sleep(3)

        try:
            mainFrame = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.navbar-inner ul a')))
            u.rc.rk_report(im, 3040, lk, vc_type=ui.get('platform'))
            logger.info('login|succ')
            return {'succ': True, 'cookies': self.d.get_cookies()}
        except Exception as e:
            logger.info('login|step1 error:验证码错误')
            u.rc.rk_report_error(lk_obj.get('Id'))
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
            # params = [self.user_info.get('id'), self.user_info.get('account'), self.user_info.get('platform'), None,
            #           False]
            # if not post_res(*params):
            logger.error('----------useless account! Post result failed!')
            # else:
            #     logger.info('useless account!(%s) Post success!' % self.user_info)

            self.d.quit()
            return {'succ': False, 'invalid_account': True}

    # 获取channel
    def get_channel(self, cookie):
        ckstr = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in cookie])
        url = 'http://xkwlm.koowo.com/muser/query'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
            'Cookie': ckstr
        }
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            logger.error('get_channel|status code %s' % res.status_code)
            return False
        res = res.content.decode('utf-8')

        yk = hp()
        yk.feed(res)
        yk.close()

        if len(yk.resArr) <= 0:
            logger.error('get_channel|error no data %s' % yk.resArr)
            return False

        logger.info('get_channel|result: %s' % yk.resArr)
        return yk.resArr

    def get_data_by_channel(self, channel, cookie, osd, oed):
        ckstr = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in cookie])
        url = 'http://xkwlm.koowo.com/muser/query'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
            'Cookie': ckstr
        }
        data = {
            'query_ptime': osd + ' 至 ' + oed,
            'query_channel': channel
        }
        res = requests.post(url, headers=headers, data=data, timeout=10)
        if res.status_code != 200:
            logger.error('get_data_by_channel|status code %s' % res.status_code)
            return False
        res = res.content.decode('utf-8')

        yk = hp1()
        yk.feed(res)
        yk.close()

        alldata = []
        for idx, td in enumerate(yk.resArr):
            tmp = {}
            if idx % 4 == 0:
                tmp['date'] = td
            elif idx % 4 == 1:
                tmp['channel'] = td
            elif idx % 4 == 2:
                tmp['activeNum'] = td
            elif idx % 4 == 3:
                tmp['money'] = td
                tmp['channelId'] = tmp['channel'].split('_')[2]  # 自己提取channelId保存
                alldata.append(tmp)
                logger.info('get_data_by_channel|alldata append:%s' % tmp)

        return alldata

    # 按查询管理子菜单分文件
    def get_data(self, cookie, osd, oed):
        channels = self.get_channel(cookie)
        for channel in channels:
            alldata = self.get_data_by_channel(channel, cookie, osd, oed)
            filepath = join(self.dir_path, '%s_%s_%s.json' % (osd, oed, channel))
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json.dumps(alldata, ensure_ascii=False))
            logger.info('get_data|文件写入成功%s' % filepath)
            time.sleep(0.5)
        return {'succ': True, 'data': channels}

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
                    return
                data_list.append({'sd': start_date, 'ed': end_date, 'data': res.get('data')})
            except Exception as e:
                logger.error(e)

        for i in data_list:
            self.d.execute_script(
                "document.querySelector('#query_ptime').value = '%s 至 %s'" % (i.get('sd'), i.get('ed')))
            self.get_img(i)

        return {'succ': True}

    def get_img(self, data):
        for channel in data.get('data'):
            change_select = """
document.querySelector('#s2id_query_channel a span').textContent= '%s';
document.querySelector('#query_channel').value= '%s';""" % (channel, channel)
            self.d.execute_script(change_select)
            self.wait_element(By.ID, 'btn-search').click()
            time.sleep(0.5)
            pic_name = '%s_%s_%s.png' % (channel, data.get('sd'), data.get('id'))
            height = self.d.execute_script("return document.body.offsetHeight")
            cut_res = cut_img(height, self.dir_path, pic_name)
            if not cut_res.get('succ'):
                logger.warning('got img failed --- named : %s\ndetail msg: %s' % (pic_name, cut_res.get('msg')))
            logger.info('got an img: %s' % pic_name)
            self.d.execute_script('document.documentElement.scrollTop=0')

