'''
cpa http://channel.360.cn/ zly
截图位置和子账号不同，需要截到渠道号
'''
from selenium.webdriver.common.by import By
import json
import time
import os

from platform_crawler.utils.utils import Util
from platform_crawler.spiders.CPA.cpa_channel_360_fc import Channel360TaskProcess
from platform_crawler.settings import join, IMG_PATH

u = Util()


# 360子账号任务类
class Channel360zong(Channel360TaskProcess):
    def __init__(self, data, **kwargs):
        print('360子账号任务类初始化')
        self.data_list = []
        super().__init__(data, **kwargs)

    # 重写登录框逻辑
    def login(self, ui):
        self.d.get('http://channel.360.cn/')
        self.d.implicitly_wait(10)
        loginBtn = self.wait_element(By.CSS_SELECTOR, '._1wpszmp05gC2wm2vtV-s3d>div a:nth-child(2)')
        loginBtn.click()
        inpUser = self.wait_element(By.CSS_SELECTOR, 'input[name="account"]')
        inpUser.clear()
        inpUser.send_keys(ui['account'])
        inpPass = self.d.find_element_by_css_selector('input[name="password"]')
        inpPass.clear()
        inpPass.send_keys(ui['password'])
        time.sleep(2)
        im, lk_obj = None, None

        try:
            # vcodeimg = self.wait_element(By.CSS_SELECTOR, '.quc-captcha-img', timeout=5)
            vcodeimg = self.d.find_element_by_css_selector('.quc-captcha-img')
            vcimgpath = join(IMG_PATH, 'app_imgs', 'channel360FatherVerifyCode.png')

            u.cutimg_by_driver(self.d, vcodeimg, vcimgpath)
            with open(vcimgpath, 'rb') as f:
                im = f.read()
            # lk = u.rc.rk_create(im, '2050').get('Result')
            lk_obj = u.rc.rk_create(im, '3000')
            lk = lk_obj.get('Result').lower()
            inpVc = self.d.find_element_by_css_selector('.quc-input-captcha')
            inpVc.send_keys(lk)
            # time.sleep(8)
        except Exception as e:
            self.logger.error('login|%s' % e)

        btnLogin = self.d.find_element_by_css_selector('input[value="登录"]')
        btnLogin.click()
        time.sleep(6)

        loginRes = self.isLogin()
        self.logger.info('isLogin:%s' % loginRes)
        if loginRes == False:
            if lk_obj:
                u.rc.rk_report_error(lk_obj.get('Id'))
            return {'succ': False, 'msg': 'login fail'}
        else:
            if im:
                u.rc.rk_report(im, 3000, lk, vc_type=ui.get('platform'))
            return {'succ': True, 'cookies': self.d.get_cookies(), 'appdict': loginRes}

    # 总账号需要抓取查看详情页中的内容
    def getDataByApp(self, app, appname):
        try:
            channelstr = self.getAppChannelSelList(app)
            sub_channel_filter = {'app': app, 'app_name': appname, 'data': []}
            res_list = []
            for sd, ed in self.dates:
                page = -1  # 当前页数
                pages = -1  # 总页数
                allChannelDetailList = []
                sub_channels = {}
                while page == -1 or page <= pages:
                    if page == -1:
                        page = 1
                    res = self.getAppByPage(app, sd, ed, channelstr, page, isDetail=True)
                    if not res:
                        self.logger.error('getAppByPage 渠道详情返回错误')
                        return {'succ': False}

                    # 渠道包过滤表
                    sub_channels.update(res.get('sub_channel_key'))

                    allChannelDetailList = allChannelDetailList + res.get('detailList')
                    self.logger.info('allChannelDetailList length:%s' % len(allChannelDetailList))
                    page = page + 1
                    pages = res.get('pages')
                    time.sleep(0.2)
                # 构造截图流程所需的数据结构
                sub_channel_filter.get('data').append({'date': [sd, ed], 'sub_channels': sub_channels})

                file_name = os.path.join(self.dir_path, '%s_%s_%s.json' % (sd, ed, appname))
                if allChannelDetailList:
                    res_list.append(1)
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(json.dumps(allChannelDetailList, ensure_ascii=False))
            return {'succ': True, 'data': sub_channel_filter, 'has_data': res_list}

        except Exception as e:
            self.logger.error(e, exc_info=1)
            return {'succ': False, 'msg': e}

    def getData(self, appdict):
        res_list = []
        for k, v in appdict.items():
            self.logger.info('getData:%s' % v)
            data = self.getDataByApp(k, v)
            if not data.get('succ'):
                continue
            res_list.extend(data.get('has_data'))
            self.data_list.append(data.get('data'))
        if len(res_list) == 0:
            self.result_kwargs['has_data'] = 0

    def get_total_img(self, app, *args):
        """
        获取总数据截图
        :param args: args like [sd, ed, app_name]
        """
        url = 'http://channel.360.cn/pay/data/%s?startDate=%s&endDate=%s&channelId=%s' % (app, args[0], args[1],
                                                                                          ','.join(self.channels))
        self.d.get(url)
        self.d.implicitly_wait(20)
        while True:
            self.getImgByPage(*args, total=True)
            if not self.getNextbtnAble():
                break
            self.d.find_element_by_css_selector('ul.pagination li:nth-child(5) span').click()

    def get_img_by_sub_channels(self, app, *args, sub_channels=None):
        """
        通过渠道包截图
        :param args: [sd, ed, app_name]
        """
        if not sub_channels:
            return {'succ': False}
        for sub_channel, sub_channel_name in sub_channels.items():
            url = 'http://channel.360.cn/pay/data/detail%s'
            params = '?app_id=%s&channel_id=%s&sub_channel_id=%s&start_date=%s&end_date=%s&is_detail=true' % (
                app, ','.join(self.channels), sub_channel, args[0], args[1])
            self.d.get(url % params)
            self.d.implicitly_wait(10)
            # ==============================
            while True:
                self.getImgByPage(*args, sub_app_name=sub_channel_name)
                if not self.getNextbtnAble():
                    break
                self.d.find_element_by_css_selector('ul.pagination li:nth-child(5) span').click()

    def getImg(self, data, *args, **kwargs):
        """
        通过渠道包按月份分别截取总数据和详细数据图片
        :param data: months data like [{'date': , 'sub_channels': }, ]
        :param args: [app, app_name]
        """
        try:
            for each_mth_data in data:
                sd, ed = each_mth_data.get('date')
                params = [args[0], sd, ed, args[1]]
                self.get_total_img(*params)
                self.get_img_by_sub_channels(*params, sub_channels=each_mth_data.get('sub_channels'))
        except Exception as e:
            self.logger.error(e, exc_info=1)
            return {'succ': False, 'msg': e}

    def get_img_process(self, *args):
        """所有截图流程"""
        for app in self.data_list:
            if not self.getAppChannelSelList(app.get('app')):      # 获取当前app_id
                continue
            self.getImg(app.get('data'), app.get('app'), app.get('app_name'))

