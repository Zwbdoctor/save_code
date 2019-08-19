'''
cpa http://wcp.taobao.com zly   淘宝对webdriver有检测，采用文博思路，不用selenium，用pyautoui定位元素
'''
from platform_crawler.utils.utils import Util
from platform_crawler.spiders.pylib.cut_img import cut_img
from platform_crawler.spiders.get_login_data.BaseModel import Base
from platform_crawler.spiders.pylib.task_process import TaskProcess
from platform_crawler.settings import IMG_PATH, join
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
import time
import os
import requests
import pyautogui
import random
import json
import re
import win32api
import win32con

report_page_url = r'https://wcp.taobao.com/partner/report.htm'
u = Util()
logger = None


slides = [
    [[1, 0, 0.09], [2, 0, 0.02], [1, 0, 0.02], [2, 0, 0.03], [1, 0, 0.01], [3, 0, 0.01], [4, 0, 0.01], [9, 0, 0.01], [5, 0, 0.01], [7, 0, 0.01], [3, 0, 0.01], [6, 0, 0.01], [2, 0, 0.01], [1, 0, 0.01], [1, 0, 0.01], [2, -1, 0.01], [1, 0, 0.01], [3, 0, 0.01], [9, 0, 0.01], [5, 0, 0.01], [4, 0, 0.01], [4, 0, 0.01], [5, 0, 0.01], [1, 0, 0.01], [6, 0, 0.1], [2, 0, 0.01], [6, 0, 0.01], [13, 2, 0.01], [9, 1, 0.01], [8, 1, 0.01], [10, 2, 0.01], [3, 1, 0.01], [1, 0, 0.01], [1, 0, 0.01], [1, 0, 0.07], [7, 0, 0.01], [8, 0, 0.01], [11, 0, 0.01], [15, 0, 0.01], [5, 0, 0.01], [3, 0, 0.01], [2, 0, 0.01], [1, 0, 0.01], [1, 0, 0.12], [1, 0, 0.01], [2, 0, 0.01], [5, 0, 0.01], [8, 0, 0.01], [4, 0, 0.01], [3, 0, 0.01], [7, 0, 0.01], [4, 0, 0.01], [3, 0, 0.01], [2, 0, 0.01], [6, 0, 0.01], [1, 0, 0.01], [2, 0, 0.01], [1, 0, 0.06], [2, 0, 0.01], [7, 0, 0.01], [4, 0, 0.01], [5, 0, 0.01], [4, 0, 0.01], [5, 0, 0.01], [3, 0, 0.01]],
    [[1, 0, 0.02], [3, 0, 0.1], [2, 0, 0.01], [3, 0, 0.01], [6, 0, 0.01], [5, 0, 0.01], [3, 0, 0.01], [4, 0, 0.01], [6, 0, 0.01], [4, -1, 0.01], [2, 0, 0.01], [4, 0, 0.01], [3, -1, 0.01], [1, 0, 0.09], [8, 0, 0.01], [9, 1, 0.01], [8, 0, 0.01], [8, 0, 0.01], [16, 1, 0.01], [5, 0, 0.01], [7, 0, 0.01], [6, 0, 0.01], [2, 0, 0.01], [1, 0, 0.01], [2, 0, 0.02], [1, 0, 0.06], [7, 3, 0.01], [6, 0, 0.01], [4, 0, 0.01], [12, 0, 0.01], [4, 0, 0.01], [2, 0, 0.01], [3, 0, 0.01], [3, 0, 0.04], [3, 0, 0.01], [6, 0, 0.01], [17, 0, 0.01], [9, 0, 0.01], [10, 0, 0.01], [9, 0, 0.01], [16, 0, 0.01], [4, 0, 0.01], [3, 0, 0.01], [1, 0, 0.06], [3, 0, 0.02], [4, 0, 0.01], [12, 0, 0.01], [6, 0, 0.01], [4, -1, 0.01], [7, 0, 0.01]],
    [[1, 0, 0.12], [2, 1, 0.01], [1, 1, 0.02], [2, 0, 0.02], [1, 0, 0.01], [3, 1, 0.01], [7, 0, 0.01], [4, 0, 0.01], [6, 1, 0.01], [7, 1, 0.01], [1, 0, 0.01], [2, 0, 0.01], [1, 0, 0.06], [2, 0, 0.01], [4, 0, 0.01], [8, 0, 0.01], [7, 0, 0.01], [5, 0, 0.01], [15, 0, 0.01], [9, 0, 0.01], [6, 0, 0.01], [8, 0, 0.01], [8, 0, 0.01], [3, 0, 0.01], [1, 0, 0.01], [5, 0, 0.01], [3, 0, 0.01], [3, 0, 0.01], [2, 0, 0.01], [7, 0, 0.01], [4, 0, 0.01], [3, 0, 0.01], [8, 1, 0.01], [2, 0, 0.01], [1, 0, 0.01], [2, 0, 0.01], [2, 0, 0.01], [2, 0, 0.01], [5, 0, 0.06], [7, 0, 0.01], [5, 0, 0.01], [16, 1, 0.01], [5, 1, 0.01], [6, 0, 0.01], [11, 0, 0.01], [4, 0, 0.01], [5, 0, 0.01], [4, 2, 0.01], [6, 0, 0.01], [1, 0, 0.01], [1, 0, 0.01], [2, 0, 0.05], [1, 0, 0.01], [3, 0, 0.01], [4, 0, 0.01], [7, 1, 0.01], [3, 0, 0.01], [3, 0, 0.01], [6, 0, 0.01], [5, 0, 0.01]],
    [[1, 0, 0.02], [2, 0, 0.01], [1, 0, 0.01], [6, 0, 0.01], [6, 0, 0.01], [6, 0, 0.01], [4, 0, 0.01], [8, 0, 0.01], [4, 0, 0.01], [2, 1, 0.01], [3, 0, 0.01], [1, 0, 0.01], [2, 0, 0.01], [4, 0, 0.01], [6, 0, 0.01], [6, 0, 0.01], [5, 0, 0.01], [7, 0, 0.01], [4, 0, 0.01], [3, 0, 0.01], [3, 0, 0.01], [4, 0, 0.01], [2, 0, 0.01], [1, 0, 0.01], [4, 0, 0.01], [3, 0, 0.01], [1, 0, 0.01], [5, 0, 0.01], [1, 0, 0.01], [3, 0, 0.01], [6, 0, 0.01], [4, 0, 0.01], [6, 0, 0.01], [6, 0, 0.01], [12, 0, 0.01], [5, 0, 0.01], [5, 0, 0.01], [6, 0, 0.01], [2, 0, 0.01], [2, 0, 0.02], [2, 0, 0.01], [3, 0, 0.01], [4, 0, 0.01], [11, 0, 0.01], [6, 0, 0.01], [7, 0, 0.01], [8, 0, 0.01], [4, 0, 0.01], [2, 0, 0.01], [3, 0, 0.01], [6, 0, 0.01], [3, 0, 0.01], [1, 0, 0.01], [4, 0, 0.01], [2, 0, 0.01], [2, 0, 0.01], [3, 0, 0.01], [3, 0, 0.01], [3, 0, 0.01], [3, 0, 0.01], [8, 0, 0.01]],
    [[2, 0, 0.02], [2, 0, 0.01], [1, 0, 0.01], [1, 0, 0.01], [2, 0, 0.03], [5, 0, 0.01], [4, 1, 0.01], [3, 0, 0.01], [6, 1, 0.01], [2, 0, 0.01], [2, 0, 0.02], [10, 0, 0.09], [4, 0, 0.01], [4, 0, 0.01], [6, 0, 0.01], [3, 0, 0.01], [2, 0, 0.02], [1, 0, 0.01], [2, 0, 0.02], [3, -1, 0.01], [1, 0, 0.01], [3, 0, 0.01], [3, 0, 0.01], [1, 0, 0.01], [1, 0, 0.01], [2, 0, 0.01], [3, 0, 0.01], [1, 0, 0.02], [5, -1, 0.05], [6, 0, 0.01], [6, 0, 0.01], [19, 0, 0.01], [11, 0, 0.01], [9, 0, 0.01], [8, 0, 0.01], [8, 0, 0.01], [3, 0, 0.01], [1, 0, 0.07], [1, 0, 0.01], [1, 0, 0.01], [6, 0, 0.01], [2, 0, 0.01], [3, 0, 0.01], [3, 0, 0.01], [5, 0, 0.01], [5, 0, 0.01], [8, 0, 0.01], [5, 0, 0.01], [16, 0, 0.01], [7, 0, 0.01], [4, 0, 0.01], [6, 0, 0.01], [4, 0, 0.01], [2, 0, 0.01], [3, 0, 0.01], [2, 0, 0.01], [3, 0, 0.01], [4, 0, 0.01], [2, 0, 0.02], [1, 0, 0.04], [6, 0, 0.02], [3, 0, 0.01], [4, 0, 0.01], [6, 0, 0.01]],
    [[1, 0, 0.06], [4, 0, 0.01], [4, 0, 0.01], [7, 0, 0.01], [2, 0, 0.01], [2, 0, 0.01], [1, 0, 0.06], [8, 3, 0.02], [4, 1, 0.01], [5, 1, 0.01], [9, 3, 0.01], [3, 0, 0.01], [2, 0, 0.01], [2, 1, 0.01], [2, 0, 0.01], [1, 0, 0.04], [1, 0, 0.01], [3, 0, 0.01], [6, 0, 0.01], [4, 2, 0.01], [2, 0, 0.01], [3, 0, 0.01], [4, 1, 0.01], [2, 0, 0.01], [1, 0, 0.07], [1, 0, 0.01], [1, 0, 0.01], [3, 0, 0.01], [1, 1, 0.01], [1, 0, 0.01], [6, 0, 0.01], [4, 0, 0.01], [5, 0, 0.01], [3, 0, 0.01], [8, 0, 0.01], [3, 0, 0.01], [5, 0, 0.01], [4, 0, 0.01], [7, 0, 0.01], [2, 0, 0.01], [3, 0, 0.01], [6, 0, 0.01], [4, 0, 0.01], [2, 0, 0.01], [9, 0, 0.01], [4, 0, 0.01], [6, 0, 0.01], [6, 0, 0.01], [13, 0, 0.01], [7, 0, 0.01], [5, 0, 0.01], [9, 0, 0.01], [2, 0, 0.01], [1, 0, 0.06], [3, 0, 0.03], [2, 0, 0.01], [3, 0, 0.01], [3, 0, 0.01], [6, 0, 0.01], [2, 0, 0.01], [2, 0, 0.01], [2, 0, 0.01], [2, 0, 0.01], [1, 0, 0.01], [1, 0, 0.01], [3, 0, 0.01], [3, 0, 0.01], [4, 0, 0.01], [4, 0, 0.01], [8, 0, 0.01]],
    [[6, 0, 0.02], [5, 0, 0.01], [17, 0, 0.01], [6, 1, 0.01], [7, 2, 0.01], [7, 0, 0.01], [10, 1, 0.01], [3, 0, 0.01], [1, 0, 0.01], [4, 0, 0.01], [1, 0, 0.01], [1, 0, 0.01], [2, 0, 0.01], [1, 0, 0.01], [1, 0, 0.01], [5, 1, 0.02], [1, 0, 0.01], [4, 0, 0.01], [8, 0, 0.01], [4, 0, 0.01], [7, 0, 0.01], [7, 0, 0.01], [11, 1, 0.01], [7, 0, 0.01], [5, 1, 0.01], [6, 1, 0.01], [10, 1, 0.01], [4, 1, 0.01], [4, 0, 0.01], [9, 0, 0.01], [3, 0, 0.01], [2, 0, 0.01], [2, 0, 0.01], [3, 0, 0.01], [2, 0, 0.01], [2, 0, 0.01], [4, 0, 0.01], [1, 0, 0.01], [1, 0, 0.01], [2, -1, 0.01], [3, 0, 0.01], [3, 0, 0.01], [4, 0, 0.01], [8, 0, 0.01], [6, 0, 0.01], [6, 0, 0.01], [12, 0, 0.01], [5, 0, 0.01], [6, 0, 0.01], [5, 0, 0.01], [10, 0, 0.01], [3, 0, 0.01], [3, 0, 0.01], [1, 0, 0.01], [5, 0, 0.01], [2, 0, 0.01]],
    [[1, 0, 0.16], [3, 0, 0.01], [4, 0, 0.01], [3, 0, 0.01], [7, 0, 0.01], [3, 0, 0.01], [2, 0, 0.01], [2, 0, 0.01], [2, 0, 0.15], [4, 0, 0.01], [7, 0, 0.01], [13, 0, 0.01], [8, 0, 0.01], [6, 0, 0.01], [9, 0, 0.01], [3, 0, 0.01], [3, 0, 0.01], [3, 0, 0.01], [2, 0, 0.01], [1, 0, 0.01], [1, 0, 0.01], [3, 0, 0.01], [1, 0, 0.01], [3, 0, 0.01], [4, 0, 0.01], [7, 0, 0.01], [4, 0, 0.01], [4, 0, 0.01], [10, 0, 0.01], [7, 0, 0.01], [6, 0, 0.01], [10, 0, 0.01], [4, 0, 0.01], [3, 0, 0.01], [5, 0, 0.01], [2, 0, 0.01], [2, 0, 0.01], [2, 0, 0.01], [3, 0, 0.01], [3, 0, 0.01], [2, 0, 0.01], [6, 0, 0.01], [2, 0, 0.01], [4, 0, 0.01], [8, 0, 0.01], [7, 0, 0.01], [4, 0, 0.01], [9, 0, 0.01], [3, 0, 0.01], [3, 0, 0.01], [6, 0, 0.01], [3, 0, 0.01], [1, 0, 0.01], [3, 0, 0.01], [3, 0, 0.01], [2, 0, 0.01], [2, 0, 0.01], [2, 0, 0.02], [3, 0, 0.02], [7, 0, 0.01], [4, 0, 0.01], [6, 0, 0.01], [5, 0, 0.01], [6, 0, 0.01], [2, 0, 0.01]],
    [[1, 0, 0.02], [4, 0, 0.01], [1, -1, 0.01], [4, 0, 0.02], [2, -1, 0.01], [3, 0, 0.01], [2, 0, 0.01], [3, -1, 0.01], [2, 0, 0.01], [3, 0, 0.01], [6, -2, 0.01], [4, 0, 0.01], [3, -1, 0.01], [4, 0, 0.01], [10, -1, 0.01], [4, 0, 0.01], [4, -1, 0.01], [9, -2, 0.01], [3, 0, 0.01], [4, -1, 0.01], [7, -1, 0.01], [14, 0, 0.01], [5, 0, 0.01], [4, 0, 0.01], [7, 0, 0.01], [3, 0, 0.01], [2, 0, 0.01], [7, 0, 0.01], [1, 0, 0.01], [4, 0, 0.01], [3, 0, 0.01], [8, 0, 0.01], [2, 0, 0.01], [4, 0, 0.01], [1, 0, 0.01], [6, 0, 0.01], [2, 0, 0.01], [3, 0, 0.01], [3, 1, 0.01], [3, 0, 0.01], [1, 0, 0.01], [3, 0, 0.01], [6, 0, 0.01], [3, 0, 0.01], [3, 0, 0.01], [2, 0, 0.01], [1, 0, 0.01], [1, 1, 0.01], [3, 0, 0.01], [2, 0, 0.01], [2, 1, 0.01], [3, 0, 0.01], [3, 0, 0.01], [3, 0, 0.01], [2, 0, 0.01], [5, 2, 0.01], [1, 0, 0.01], [3, 0, 0.01], [2, 1, 0.01], [4, 1, 0.01], [3, 2, 0.01], [1, 0, 0.01], [5, 1, 0.01], [2, 0, 0.01], [3, 0, 0.01], [2, 0, 0.01], [5, 0, 0.01], [2, 0, 0.01], [1, 1, 0.01], [3, 0, 0.02], [1, 0, 0.01], [2, 1, 0.01], [3, 0, 0.01], [3, 0, 0.01], [2, 0, 0.01], [8, 1, 0.01], [7, 0, 0.01], [5, 0, 0.01]],
]


class TaobaoSpider(TaskProcess, Base):
    def __init__(self, user_info, **kwargs):
        self.page_dict = {
            'pst': 3,
            'delete_host_cookie': [
                '.taobao.com', 'g.alicdn.com', '.mmstat.com', 'login.taobao.com', '.login.taobao.com'
            ],
            'url': 'https://login.taobao.com/member/login.jhtml?redirectURL=https%3A%2F%2Fwcp.taobao.com%2Fhomepage.htm'
        }
        global logger
        super().__init__(is_cpa=True, user_info=user_info, **kwargs)
        logger = self.logger

    def init_driver_new_version(self):
        self.open_remote_debug_chrome(use_proxy=True, proxy_server='47.102.221.66:8889')
        # self.open_remote_debug_chrome(use_proxy=True)
        co = ChromeOptions()
        co.add_argument('log-level=3')
        co.add_argument('--disable-infobars')
        co.add_argument('--ignore-certificate-errors')
        # co.debugger_address = '127.0.0.1:9222'
        self.d = webdriver.Chrome(options=co)
        self.d.set_page_load_timeout(60)
        self.d.set_script_timeout(30)

    # 从html页面中提取出arr
    def decodeApps(self, content):
        self.gApps = {}
        try:
            data = re.search(r'(\[\{.*\}\]);', content).group(1)
        except:
            logger.error('decodeApps提取失败')
            return False
        res = json.loads(data)
        if isinstance(res, list):
            for item in res:
                self.gApps[item.get('id')] = item.get('name')
            logger.info('decodeApps成功:%s' % self.gApps)
            return True
        else:
            logger.error('decodeApps提取失败')
            return False

    def isLogin(self, cks):
        url = report_page_url
        ckstr = '; '.join(['%s=%s' % (e['name'], e['value']) for e in cks])
        headers = {
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            'cookie': ckstr,
            'referer': "https://login.taobao.com/member/login.jhtml?redirectURL=https%3A%2F%2Fwcp.taobao.com%2Fhomepage.htm",
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3569.0 Safari/537.36'
        }
        res = requests.get(url, headers=headers, verify=False)
        logger.info('isLogin status_code:%s' % res.status_code)
        if res.status_code == 200:
            if not self.decodeApps(res.text):
                return False
            return True
        else:
            return False

    def clear(self):
        for i in range(0, 30):
            win32api.keybd_event(8, 0, 0, 0)
            win32api.keybd_event(8, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.05)

    def move_to(self, length):
        # tracks = self.get_tracks(length, None)
        x, y = u.pag.position()
        from pyautogui._pyautogui_win import _moveTo
        dstx = x + length
        for px, py, slpt in random.choice(slides):       # 按增量滑动滑块
            x += px
            # u.pag.moveRel(xOffset=px, yOffset=py)
            _moveTo(x, py)
            if x > dstx:
                _moveTo(dstx, y)
                break
            time.sleep(slpt)
        else:
            u.pag.moveTo(dstx, y)

    def login_with_remote_chrome(self):
        self.init_browser()
        url = 'https://login.taobao.com/member/login.jhtml?redirectURL=https%3A%2F%2Fwcp.taobao.com%2Fhomepage.htm'
        self.d.get(url)
        self.d.find_element_by_id('TPL_username_1').send_keys(self.acc)
        self.d.find_element_by_id('TPL_password_1').send_keys(self.pwd)
        self.d.find_element_by_id('J_SubmitStatic').click()

    def login(self):
        try:
            self.sys_opera(self.page_dict.get('url'), self.page_dict.get('delete_host_cookie'))
            time.sleep(2)
            taobao_img_path = join(IMG_PATH, 'taobaoimg')
            _join = join

            try:
                passloginPos = u.btn_location(_join(taobao_img_path, 'passlogin.png'))
                x, y = passloginPos
                pyautogui.click(x + 100, y)
                # pyautogui.click(x, y)
                logger.info('x%s, y%s' % (x, y))
                time.sleep(1)
            except:
                # 有时候打开会直接是密码页面，没有切换按钮
                logger.error('login|passlogin按钮没有找到')

            if not u.click_img_center(_join(taobao_img_path, 'username.png')):
                return {'succ': False, 'msg': 'not found img location: username.png'}
            self.clear()
            pyautogui.typewrite(self.acc, interval=0.3)
            pyautogui.hotkey('esc')
            time.sleep(1)

            u.click_img_center(_join(taobao_img_path, 'password.png'))
            self.clear()
            pyautogui.typewrite(self.pwd, interval=0.3)
            pyautogui.hotkey('esc')
            time.sleep(2)

            u.click_img_center(_join(taobao_img_path, 'loginbtn.png'))
            location = u.btn_location(_join(taobao_img_path, 'verify_slip_button.png'), loop_time=3)
            if location:
                for e in range(3):
                    # duration = random.uniform(1.2, 1.9)
                    u.click_img_center(_join(taobao_img_path, 'password.png'))
                    self.clear()
                    pyautogui.typewrite(self.pwd, interval=0.3)
                    pyautogui.mouseDown(x=location[0], y=location[1])
                    self.move_to(266)
                    # pyautogui.moveTo(x=location[0]+266, y=location[1], duration=duration, tween=pyautogui.easeOutQuart)
                    pyautogui.mouseUp()
                    u.click_img_center(_join(taobao_img_path, 'loginbtn.png'))
                    location = u.btn_location(_join(taobao_img_path, 'verify_slip_button.png'), loop_time=3)
                    if not location:
                        break

            time.sleep(3)

            need_host = ['.taobao.com', '.mmstat.com']
            cks = self.getCookies(need_host, ck_type='json')
            if not cks.get('succ'):
                return cks
            cks = cks.get('msg')
            loginres = self.isLogin(cks)
            if loginres == False:
                return {'succ': False}
            else:
                self.kill_chrome()
                time.sleep(1)
                return {'succ': True, 'cookies': cks}
        except Exception as e:
            logger.error('login error: %s' % e, exc_info=1)
            return {'succ': False, 'msg': e}

    # 登录重试
    def runLogin(self, ui):
        res = None
        for e in range(1, 6):
            res = self.login()
            if res['succ']:
                return res
            else:
                time.sleep(3)
                self.kill_chrome()
        else:
            # 上报无效
            # params = [self.user_info.get('id'), self.user_info.get('account'), self.user_info.get('platform'), None,
            #           False]
            # if not post_res(*params):
            #     logger.error('----------useless account! Post result failed!')
            # else:
            logger.info('useless account!(%s) Post success!' % self.user_info)
            return {'succ': False, 'invalid_account': True}

    def getDataByApp(self, appkey, appname, cookie, osd, oed):
        ckstr = '; '.join(['%s=%s' % (e['name'], e['value']) for e in cookie])
        logger.info('getDataByApp|%s start osd:%s oed:%s ckstr:%s' % (appname, osd, oed, ckstr))
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'cookie': ckstr,
            'referer': report_page_url,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
        }
        url = r'https://wcp.taobao.com/partner/chart.htm?chartType=1&fromDate=%s&toDate=%s&appKey=%s&channelIds=' % (
        osd, oed, appkey)
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            return {'succ': False, 'data': 'status code not 200'}
        res = res.content.decode('utf-8')
        logger.info('app：%s request succ' % appname)
        return {'succ': True, 'data': res}

    # 按app分文件记录
    def get_data(self, cookies, days):
        res_list = []
        for start_date, end_date in days:
            # apps = self.getApps(cookies)
            apps = self.gApps
            for appkey in apps:
                file_name = os.path.join(self.dir_path, '%s_%s_%s.json' % (start_date, end_date, apps.get(appkey)))
                res = self.getDataByApp(appkey, apps.get(appkey), cookies, start_date, end_date)
                if res.get('data'):
                    res_list.append(1)
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(res.get('data'))
                time.sleep(0.25)
        if not res_list:
            self.result_kwargs['has_data'] = 0

    def openPageAfterLogin(self, cookies):
        logger.info('openPageAfterLogin|start|cookie:%s' % cookies)
        self.init_browser()
        url = 'https://wcp.taobao.com'
        self.d.get(url)
        self.d.implicitly_wait(5)
        for ck in cookies:
            self.d.add_cookie(ck)
        self.d.get(url)
        self.d.implicitly_wait(5)
        return True

    def get_into(self):
        self.d.implicitly_wait(5)
        self.wait_element(By.LINK_TEXT, '激活').click()
        self.wait_element(By.LINK_TEXT, '数据报表').click()
        self.d.implicitly_wait(5)

    def getImg(self, sd, ed):
        self.d.execute_script("document.querySelector('#start').value='%s'" % sd)
        self.d.execute_script("document.querySelector('#end').value='%s'" % ed)
        self.d.execute_script("document.querySelector('#query1').click()")
        self.d.find_element_by_css_selector('.mutl-select-trigger').click()
        channels_ele = self.d.find_elements_by_css_selector('.checkbox-inline')
        channels = [x.text.strip() for x in channels_ele]
        for aid, app in self.gApps.items():
            self.d.execute_script("document.querySelector('#app').value='%s'" % aid)
            for c in channels:
                self.d.execute_script("document.querySelector('.mutl-select-trigger').value='%s'" % c)
                self.d.find_element_by_id('query1').click()
                pic_name = '%s_%s_%s_%s.png' % (app, c, sd, ed)
                height = self.d.execute_script('return document.documentElement.offsetHeight')
                cut_res = cut_img(None, self.dir_path, pic_name)      # 截图保存
                if not cut_res['succ']:
                    logger.error('get img %s failed-------msg: %s' % (pic_name, cut_res.get('msg')))
                logger.info('height: %s ---picname: %s' % (height, pic_name))

    def login_and_get_data(self, ui):
        # 获取时间
        mths, days = u.make_dates(ms=None, ys=None, ye=None, me=None)
        self.pwd = ui.get('password')

        # 登陆
        login_res = self.runLogin(ui)
        if not login_res['succ']:
            return login_res
        cookies = login_res.get('cookies')

        self.kill_chrome()
        # selenium通过登录的cookie打开report页
        openRes = self.openPageAfterLogin(cookies)
        if openRes == False:
            return openRes

        # 获取上个月到现在每天的数据
        self.get_data(cookies, days)

        # 截图
        self.get_into()
        self.d.implicitly_wait(5)
        for sd, ed in days:
            self.getImg(sd, ed)

        return {'succ': True}
