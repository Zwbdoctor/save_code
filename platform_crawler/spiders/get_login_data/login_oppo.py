"""
index:get sessionid, k,tk, captcha:update k, tk;  post: vc, un, pwd   + cookies
"""
import time
import os
import logging
import random
from selenium import webdriver
from PIL import Image
from pyautogui._pyautogui_win import _moveTo

from platform_crawler.utils.utils import Util
from platform_crawler.settings import BASEDIR

u = Util()
_join = os.path.join
VERIFY_IMAGE_PATH = os.path.join(BASEDIR, 'imgs', 'oppo_imgs', 'vc.jpg')
VERIFY_BOX_PATH = _join(BASEDIR, 'imgs', 'oppo_imgs', 'slip_box.png')
logger = None

slides = [
    [[2, 1, 16], [2, 0, 14], [3, 0, 2], [3, 0, 9], [3, 1, 8], [4, 0, 9], [4, 0, 8], [5, 0, 9], [6, 0, 5], [8, 0, 12], [6, 0, 6], [8, 0, 10], [22, 0, 25], [5, 0, 10], [5, 0, 2], [4, 0, 7], [3, 0, 13], [3, 0, 4], [4, 0, 16], [4, 0, 15], [3, 0, 1], [4, 0, 12], [3, 0, 3], [4, 0, 11], [2, 0, 5], [3, 0, 13], [3, 0, 3], [3, 0, 14], [1, 0, 3], [5, 2, 15], [3, 0, 17], [6, 0, 17], [5, 0, 15], [6, 0, 15], [2, 0, 16], [2, 0, 3], [1, 0, 6], [2, 0, 9], [1, 0, 7], [3, 0, 10], [1, 0, 6], [2, 0, 10], [1, 0, 6], [2, 0, 8], [2, 0, 8], [1, 0, 8], [1, 0, 8], [1, 0, 9], [2, 0, 8], [1, 1, 15], [1, 0, 16], [1, 0, 14], [1, 0, 2], [1, 0, 13], [1, 0, 3], [1, 0, 13], [2, 0, 3], [1, 0, 16], [1, 0, 101], [1, 0, 50], [1, 1, 16], [1, 0, 233], [1, 0, 23], [1, 1, 127], [1, 0, 167], [1, 0, 349]],
    [[0, 0, 85], [1, 0, 55], [1, 0, 12], [1, 0, 19], [3, 0, 16], [5, 0, 17], [3, 0, 16], [5, 0, 17], [5, 0, 17], [5, 1, 17], [6, 0, 18], [5, 0, 17], [6, 0, 16], [14, 1, 18], [9, 1, 16], [6, 0, 17], [5, 0, 18], [5, 0, 16], [5, 0, 17], [4, 0, 17], [4, 0, 18], [4, 0, 16], [5, 0, 17], [2, 0, 17], [5, 0, 18], [4, 0, 17], [4, -1, 15], [5, 0, 18], [3, 0, 17], [5, -1, 17], [4, 0, 17], [6, 0, 17], [3, 0, 16], [3, -1, 17], [3, 0, 17], [2, 0, 17], [5, -1, 19], [4, 0, 14], [5, 0, 18], [6, -1, 17], [4, -1, 17], [2, 0, 17], [4, -1, 17], [3, 0, 17], [1, 0, 17], [1, 0, 27], [2, 0, 24], [1, 0, 17], [2, 0, 18], [1, 0, 15], [0, 0, 131], [-1, 0, 175], [-1, 0, 92], [-1, 0, 79], [0, 0, 174], [-1, 0, 27]],
    [[3, 0, 16], [4, 0, 20], [5, 0, 13], [4, -1, 17], [5, 0, 17], [4, -1, 17], [5, 0, 17], [9, 0, 18], [7, 0, 17], [6, 0, 17], [7, 0, 17], [6, 0, 16], [6, 0, 17], [6, 0, 17], [6, 0, 17], [11, 0, 17], [7, 0, 18], [6, 0, 16], [6, 0, 17], [6, 0, 17], [5, 0, 18], [5, 0, 16], [4, 0, 18], [7, 0, 17], [3, 0, 16], [3, 0, 16], [3, 0, 19], [4, 0, 16], [2, 0, 16], [4, 0, 17], [3, 0, 17], [2, -1, 16], [3, 0, 17], [3, 0, 18], [2, 0, 16], [1, 0, 17], [1, 0, 47], [1, -1, 30], [1, 0, 72], [1, 0, 22], [1, 0, 43], [1, 0, 31], [1, 0, 24], [1, 0, 20], [1, 0, 69], [1, 0, 16], [1, 0, 16], [1, 0, 17], [1, 0, 17]],
    [[3, 0, 20], [6, 0, 18], [11, 0, 16], [14, 2, 16], [23, 2, 17], [12, 1, 17], [10, 0, 17], [7, 0, 19], [5, 0, 15], [5, 0, 17], [6, 0, 17], [6, 0, 17], [9, 0, 17], [6, 0, 17], [7, 0, 17], [5, 0, 18], [7, 0, 17], [8, 0, 16], [9, 0, 18], [6, 0, 16], [7, 0, 17], [1, 0, 16], [2, 0, 18], [5, 0, 16], [7, 0, 17], [6, 0, 17], [5, 0, 17], [1, 0, 17], [-1, 0, 204], [-1, 0, 19], [-1, 0, 15]],
    [[5, 0, 17], [9, 0, 17], [8, 0, 17], [7, 0, 16], [6, 0, 17], [7, 0, 18], [6, 0, 16], [6, -1, 17], [10, 0, 17], [7, -1, 18], [6, 0, 17], [5, 0, 15], [6, -1, 18], [6, -1, 18], [6, 0, 16], [8, -1, 17], [4, 0, 17], [5, 0, 16], [4, 0, 18], [4, 0, 17], [5, 0, 16], [4, 0, 18], [5, 0, 18], [3, 0, 16], [5, 0, 17], [3, 0, 16], [2, 0, 19], [3, 0, 16], [2, 0, 17], [2, 0, 15], [1, 0, 20], [1, 0, 17], [2, 0, 15], [1, 0, 73], [1, 0, 28], [1, 0, 17], [1, 0, 17], [1, 0, 17], [1, 0, 17], [1, 0, 17], [1, 0, 17], [2, 0, 17], [2, 0, 17], [1, 0, 16], [1, 0, 84], [1, 0, 304], [1, 0, 31], [1, 0, 32]],
    [[1, 0, 33], [1, 0, 18], [1, 0, 15], [2, 0, 16], [3, 0, 17], [6, 0, 18], [5, 0, 16], [6, 0, 17], [7, 0, 16], [7, 1, 18], [9, 1, 17], [5, 0, 16], [5, 0, 18], [6, 0, 17], [4, 0, 17], [3, 0, 18], [5, 0, 16], [7, 0, 17], [6, 0, 17], [5, 0, 17], [4, 0, 16], [5, 0, 18], [3, 1, 16], [4, 0, 17], [7, 0, 17], [5, 0, 17], [8, 0, 17], [6, 0, 18], [7, 1, 17], [6, 0, 18], [5, 0, 16], [4, 0, 16], [5, 0, 17], [2, 0, 17], [4, 0, 18], [3, 0, 16], [2, 0, 18], [2, 0, 16], [1, 0, 19], [1, 0, 14], [1, 0, 18], [1, 0, 17], [1, 0, 210], [2, 0, 27], [1, 0, 17], [1, 0, 18], [1, 0, 16], [1, 0, 17], [-1, 0, 377], [-1, 0, 16], [-1, 0, 23], [-1, 0, 24], [0, 1, 119], [1, 0, 17], [1, 0, 129]],
    [[1, 0, 50], [1, 0, 17], [1, 0, 17], [1, 0, 17], [2, 0, 17], [5, 0, 17], [8, 0, 16], [11, 0, 17], [12, 0, 18], [15, 0, 16], [18, 0, 18], [10, 0, 17], [8, 0, 17], [7, -1, 17], [5, 0, 17], [6, 0, 17], [4, 0, 17], [6, 0, 17], [7, 0, 17], [5, -1, 16], [3, 0, 17], [3, 0, 17], [2, 0, 17], [1, 0, 16], [1, -1, 18], [2, 0, 17], [1, 0, 17], [2, 0, 17], [1, 0, 17], [2, 0, 17], [1, 0, 17], [2, 0, 17], [1, 0, 17], [1, 0, 18], [1, 0, 16], [1, 0, 49], [1, 0, 23], [1, 0, 25], [1, 0, 21], [1, 0, 27], [1, 0, 24], [1, 0, 17], [1, 0, 23], [1, 0, 16], [1, 0, 17], [1, 0, 15], [1, 0, 56], [1, 0, 56], [1, 0, 24], [1, 0, 209], [1, 0, 31], [1, 1, 96], [1, 0, 40]],
    [[1, 0, 43], [1, 0, 18], [1, 0, 17], [3, 0, 17], [5, 0, 17], [9, 0, 17], [9, 0, 17], [8, 0, 16], [8, 0, 18], [10, 0, 16], [11, 0, 18], [11, 0, 17], [10, 0, 17], [11, 0, 16], [7, 0, 18], [6, 0, 17], [6, 0, 17], [6, 0, 17], [5, 0, 16], [4, 0, 17], [6, 0, 16], [8, 0, 18], [16, 0, 17], [8, 0, 16], [5, 0, 18], [2, -1, 17], [1, 0, 221], [1, 0, 104], [1, 0, 15], [1, 0, 18], [1, 0, 15], [1, 0, 127], [1, 0, 361]],
    [[2, 0, 29], [5, 0, 16], [6, 0, 18], [6, 0, 18], [15, 0, 16], [12, 1, 17], [9, 0, 17], [8, 0, 16], [6, 0, 17], [6, 0, 17], [6, 0, 18], [6, -1, 17], [10, -2, 17], [6, 0, 16], [5, -1, 17], [4, 0, 18], [2, 0, 17], [3, 0, 16], [3, 0, 18], [4, 0, 17], [7, 0, 17], [4, 0, 15], [3, 0, 18], [4, 0, 16], [3, 0, 18], [4, 0, 17], [4, 0, 17], [4, 0, 17], [2, 0, 16], [4, 0, 18], [3, 0, 17], [3, 0, 16], [2, 0, 17], [3, 0, 18], [1, 0, 16], [1, 0, 17], [1, 0, 17], [1, 0, 18], [2, 0, 16], [2, 0, 18], [2, 0, 17], [1, 0, 17], [1, 0, 85]],
    [[1, 0, 15], [5, 0, 16], [10, 0, 16], [14, 0, 18], [18, 0, 17], [15, 0, 16], [13, 0, 17], [17, 0, 23], [6, -1, 12], [14, 0, 16], [8, 0, 17], [8, -1, 18], [4, -1, 17], [3, 0, 16], [1, 0, 18], [1, 0, 17], [1, -1, 16], [2, 0, 18], [0, -1, 17], [1, 0, 18], [1, 0, 33], [1, 0, 16], [1, 0, 18], [1, -1, 17], [1, 0, 16], [2, 0, 17], [3, 0, 17], [4, -1, 16], [2, 0, 18], [3, 0, 17], [2, 0, 68], [1, 0, 17], [2, 0, 16], [1, 0, 17], [1, 0, 17], [1, 0, 67], [1, 0, 33], [1, 0, 19], [2, 0, 33], [1, 0, 86], [1, 0, 272], [1, 0, 155]],
    [[1, 0, 23], [1, 0, 16], [1, 0, 16], [7, 0, 17], [6, 0, 17], [8, 0, 17], [9, 0, 18], [10, 0, 17], [9, 0, 16], [9, 0, 17], [7, 0, 17], [13, -2, 16], [9, -1, 19], [7, 0, 16], [7, -1, 17], [5, 0, 16], [6, 0, 18], [5, 0, 16], [5, 0, 20], [8, 0, 16], [4, -1, 17], [5, 0, 17], [3, 0, 16], [4, 0, 18], [4, 0, 17], [4, 0, 16], [6, 0, 17], [5, 0, 17], [2, 0, 17], [1, 0, 18], [0, -1, 16], [1, 0, 17], [1, 0, 17], [1, 0, 16], [1, 0, 17], [1, 0, 68], [1, 0, 34], [0, -1, 34], [1, 0, 17], [1, 0, 17], [1, 0, 35], [1, 0, 17], [1, 0, 34], [1, 0, 34], [1, 0, 17], [1, 0, 32], [1, 0, 101], [1, 0, 86], [1, 0, 18], [1, 0, 68], [1, 0, 31]]
]


class Oppo:

    def __init__(self, user_info, log_name):
        global logger
        logger = logging.getLogger(log_name)
        self.d = None
        self.acc = user_info.get('account')
        self.pwd = user_info.get('password')
        self.user_info = user_info

    def init_driver(self):
        self.d = webdriver.Chrome()
        self.d.set_page_load_timeout(60)  # 页面超时时间
        self.d.set_script_timeout(30)  # js加载超时时间
        self.d.maximize_window()
        return self.d

    def get(self, url):
        try:
            self.d.delete_all_cookies()
            self.d.get(url)
        except:  # 超时重试一次
            self.d.delete_all_cookies()
            self.d.get(url)
        time.sleep(3)

    def cut_bg_imgs(self):
        abs_height = self.d.execute_script('return h=window.outerHeight-window.innerHeight')
        el = self.d.find_element_by_id('dx_captcha_basic_slider_1')
        x = el.location['x']
        y = el.location['y']
        width = el.size['width']
        height = el.size['height']
        x = width / 2 + x
        y = height / 2 + y
        start_point = (x, y + abs_height)
        u.pag.mouseDown(*start_point)
        bg = self.d.find_element_by_css_selector('#dx_captcha_basic_bg_1 canvas')
        bg_x = bg.location['x']
        bg_y = bg.location['y']
        bg_w = bg.size['width']
        bg_h = bg.size['height']
        time.sleep(0.5)
        u.pag.screenshot(VERIFY_IMAGE_PATH, (bg_x + 65, bg_y + abs_height, bg_w, bg_h))
        time.sleep(0.2)
        u.pag.mouseUp()
        return start_point

    def cut_sliper(self):
        # 拦截url，
        from re import sub
        from requests import get
        sliper_ele = self.d.find_element_by_css_selector('#dx_captcha_basic_sub-slider_1 img').get_attribute('src')
        headers = {
            'Accept': "*/*",
            'Host': "captcha-sec.oppomobile.com",
            'accept-encoding': "gzip, deflate",
            'Connection': "keep-alive",
            'Referer': "https://e.oppomobile.com/market/login/index.html?redirect=https%3A%2F%2Fe.oppomobile.com%2Fmarket%2Findex.html",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
        }
        nt = int(time.time() * 1000)
        sliper_url = sub(r'aid=dx-(\d+)-', 'aid=dx-%s-' % str(nt), sliper_ele)
        try:
            resp = get(sliper_ele, headers=headers, timeout=20)
            if not resp.content:
                return {'succ': False, 'msg': 'none img'}
            with open(VERIFY_BOX_PATH, 'bw') as i:
                i.write(resp.content)
            im = Image.open(VERIFY_BOX_PATH)
            out = im.resize((53.6, 50.25))
            out.save(VERIFY_BOX_PATH)
        except:
            logger.error('get slip_box image time out')
            return {'succ': False}

    def cut_imgs(self):
        res = self.cut_sliper()
        if res.get('msg') == 'none img':
            time.sleep(2)
            self.login()
        start_point = self.cut_bg_imgs()
        return start_point

    def slip_the_box(self, length, start_point):
        line = random.choice(slides)
        u.pag.mouseDown(x=start_point[0], y=start_point[1])
        for x, y, slp in line:
            x += start_point[0]
            _moveTo(x, y)
            time.sleep(slp / 100)
            if x > (length + start_point[0]):
                break
        else:
            _moveTo(start_point[0] + length, start_point[1])
        u.pag.mouseUp()

    def deal_verify_code(self, start_point):
        from platform_crawler.spiders.pylib.slip_py import vc_location
        res = vc_location(VERIFY_BOX_PATH, VERIFY_IMAGE_PATH)
        x = int(res[0]) + 65
        self.slip_the_box(x, start_point)

    def login(self):
        url = 'https://e.oppomobile.com/login'
        self.get(url)
        # start_point = self.cut_imgs()
        self.d.find_element_by_css_selector('input[placeholder="用户名"]').send_keys(self.acc)
        self.d.find_element_by_css_selector('input[placeholder="密码"]').send_keys(self.pwd)
        # self.d.find_element_by_css_selector('.btn-submit').click()
        try:
            self.d.implicitly_wait(40)
            self.d.find_element_by_css_selector('.title.font_wg')
            self.d.implicitly_wait(3)

            cookies = self.d.get_cookies()
            logger.info('login success')
            return {'succ': True, 'cookies': cookies, 'driver': self.d}
        except:
            logger.info('login failed')
            self.d.quit()
            return {'succ': False, 'msg': 'login failed after 5 times', 'invalid_account': True}

    def run_login(self):
        self.d = self.init_driver()
        try:
            return self.login()
        except Exception as er:
            logger.error(er, exc_info=1)
            self.d.quit()
            return {'succ': False, 'msg': 'got an error with unknown reason'}
