from platform_crawler.utils.utils import Util
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.spiders.pylib.task_process import TaskProcess

import json
import time
import os
import requests

u = Util()


# 360任务父类
class Channel360TaskProcess(TaskProcess):
    def __init__(self, data, **kwargs):
        self.channels = None
        self.dates = None
        self.cookies = []
        self.cookies_str = None
        print('360任务父类初始化')
        super().__init__(is_cpa=True, user_info=data)

    # 检验是否登录成功，cookie存储的只是sessionId;成功之后获取app_list
    def isLogin(self):
        url = 'http://channel.360.cn/frontend/data/app-list'
        cookie = self.d.get_cookies()
        cookie = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in cookie])
        header = {
            'Cookie': cookie,
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
        }
        try:
            testres = requests.get(url, headers=header, allow_redirects=False, timeout=60)
        except:
            return False
        if testres.status_code != 200:
            return False
        testres = testres.json()
        if testres.get('error') == 0:
            return testres.get('data')
        else:
            return False

    # 被子类重写
    def login(self, ui):
        return

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
            # params = [ui.get('id'), ui.get('account'), ui.get('platform'), None,
            #           False]
            # if not post_res(*params):
            # self.logger.error('----------useless account! Post result failed!')
            # else:
            self.logger.info('Useless account!(%s) Ready to post result!' % ui)

            self.d.quit()
            return {'succ': False, 'invalid_account': True}

    def getAppChannelSelList(self, app):
        url = 'http://channel.360.cn/frontend/data/index?app_id=%s' % app
        cookiestr = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in self.cookies])
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Cookie': cookiestr
        }
        res = None
        try:
            res = requests.get(url, headers=headers, timeout=60)
        except Exception as e:
            self.logger.warning(e, exc_info=1)
            return False
        if res.status_code != 200:
            self.logger.error(
                'getAppChannelSelList|error status_code not 200, %s, ui:%s' % (res.status_code, self.user_info))
            return False
        res = res.content.decode('utf-8')
        res = json.loads(res)
        channelarr = []
        for channelkey in res.get('data').get('select_list'):
            channelarr.append(channelkey)
        channelstr = ",".join(channelarr)
        self.logger.info('getAppChannelSelList channelstr：%s' % channelarr)
        self.channels = channelarr
        return channelstr

    def getAppByPage(self, app, sd, ed, channelstr, page, isDetail=0):
        self.logger.info(
            'getAppByPage|start app:%s sd:%s ed:%s channelstr:%s page:%s' % (app, sd, ed, channelstr, page))
        url = 'http://channel.360.cn/frontend/data/index?app_id=%s&start_date=%s&end_date=%s&channel_id=%s&is_detail=%s&page=%s' % (
        app, sd, ed, channelstr, isDetail, page)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Cookie': self.cookies_str
        }
        es = None       # 超时重试2次
        for e in range(3):
            try:
                res = requests.get(url, headers=headers, timeout=60)
                break
            except Exception as es:
                continue
        else:
            self.logger.error(es, exc_info=1)
            return False
        if res.status_code != 200:
            self.logger.error('getAppByPage|error status_code not 200, %s, ui:%s' % (res.status_code, self.user_info))
            return False
        res = res.content.decode('utf-8')
        res = json.loads(res)
        if (not res) or (not res.get('data')) or (not isinstance(res.get('data').get('detail_list'), list)):
            self.logger.error('getAppByPage|error has not data:%s, ui:%s' % (res, self.user_info))
            return False
        sub_keys = res.get('data').get('select_list')
        data_list = [e.get('sub_channel_name') for e in res.get('data').get('detail_list')]
        keys = {k: v for k, v in sub_keys.items() if v in data_list}
        return {
            'detailList': res.get('data').get('detail_list'), 'sub_channel_key': keys,
            'pages': res.get('data').get('pages')
        }

    def get_img_process(self, app_dict):
        """Overwrite by child class"""
        pass

    def getData(self, *args, **kwargs):
        """Overwrite by child class"""
        pass

    def login_and_get_data(self, ui):
        ys, ms, ye, me = ui.get('dates') if ui.get('dates') else (None, None, None, None)
        mths, self.dates = u.make_dates(ys=ys, ms=ms, ye=ye, me=me)
        # 登陆
        login_res = self.runLogin(ui)
        if not login_res['succ']:
            return login_res
        self.cookies = login_res.get('cookies')
        self.cookies_str = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in self.cookies])
        appdict = login_res.get('appdict')

        # 请求获取数据
        self.getData(appdict)

        # 截图
        self.get_img_process(appdict)
        return {'succ': True}

    def getNextbtnAble(self):
        from selenium.common.exceptions import TimeoutException
        try:
            self.d.implicitly_wait(3)
            time.sleep(1)
            nextbtn = self.d.find_elements_by_css_selector('ul.pagination li')
            if nextbtn[-2].get_attribute('class').strip() == 'disabled':
                raise Exception('next button is disabled')
            isNextbtnAble = True  # 下一页按钮
        except TimeoutException:
            return False
        except Exception as e:
            isNextbtnAble = False
        self.logger.info('getNextbtnAble: %s' % isNextbtnAble)
        return isNextbtnAble

    def getImgByPage(self, *args, total=False, **kwargs):
        # 获取当前页码
        try:
            self.d.implicitly_wait(3)
            time.sleep(1.5)
            page = self.d.find_element_by_css_selector('.active a[role="button"]').text.strip()
        except:
            page = '1'
        # 截图
        self.d.execute_script('document.documentElement.scrollTop=0;')
        has_data = self.d.find_element_by_css_selector('div.table-wrap > table > tbody > tr > td').text
        if has_data == '暂无数据':
            return
        if total:
            page = 'total%s' % page
        self.cut_img_(*args, page=page, **kwargs)

    def cut_img_(self, sd, ed, keyname, page='1', pic_name=None, sub_app_name=None):
        """
        截图
        :param keyname: 应用名
        :param page: 页数，或渠道包名
        :param pic_name:
        :return: None
        """
        self.d.execute_script('document.documentElement.scrollTop=0;')
        time.sleep(0.5)
        if not pic_name:
            name_params = [sd, ed, keyname, page] if not sub_app_name else [sd, ed, keyname, sub_app_name, page]
            pic_name = '%s.png' % ('_'.join(name_params))
        height = self.d.execute_script(r'return document.body.offsetHeight') + 84
        cut_res = cut_img(height, self.dir_path, pic_name)
        if not cut_res.get('succ'):
            self.logger.error(
                'cut picture failed, possible msg:\ndir_path:%s\npic_name: %s' % (self.dir_path, pic_name))
        self.logger.info('got a picture: pic_msg: %s' % os.path.join(self.dir_path, pic_name))
        time.sleep(2)

    # 子账号截图流程
    def getImg(self, key, keyname, *args, **kwargs):
        try:
            for sd, ed in self.dates:
                cid = ','.join(self.channels)
                url = 'http://channel.360.cn/pay/data/%s?startDate=%s&endDate=%s&channelId=%s' % (key, sd, ed, cid)
                self.d.get(url)
                self.d.implicitly_wait(5)
                while True:
                    self.getImgByPage(sd, ed, keyname)
                    if not self.getNextbtnAble():
                        break
                    self.d.find_element_by_css_selector('ul.pagination li:nth-child(5) span').click()
                    time.sleep(3)
            else:
                return {'succ': True, 'msg': 'img got success'}
        except Exception as e:
            self.logger.error(e, exc_info=1)
            return {'succ': False, 'msg': e}
