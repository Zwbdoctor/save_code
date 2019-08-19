from selenium import webdriver
from selenium.webdriver import ActionChains
from scipy.interpolate import interp1d
from numpy import arange, array
# from selenium.webdriver.common.by import By
import random
import time
import logging
import math

from platform_crawler.send_keys_win32.sendkeys import mouse_move
from platform_crawler.utils.utils import Util
from platform_crawler.utils.post_get import get
from platform_crawler.settings import IMG_PATH, join

u = Util()
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


class MeiZu:

    def __init__(self, user_info, log_name):
        global logger
        self.d = None
        self.acc = user_info.get('account')
        self.pwd = user_info.get('password')
        self.user_info = user_info
        logger = logging.getLogger(log_name)

    def init_driver(self):
        driver = webdriver.Chrome()
        driver.set_page_load_timeout(60)
        driver.set_script_timeout(30)
        driver.maximize_window()
        self.act = ActionChains(driver)
        return driver

    def get(self, url):
        try:
            self.d.delete_all_cookies()
            self.d.get(url)
        except:  # 超时重试一次
            self.d.delete_all_cookies()
            self.d.get(url)
        time.sleep(3)

    def get_vc_img(self):
        try:
            url = self.d.find_element_by_class_name('geetest_item_img').get_attribute('src')
        except:
            return {'succ': False, 'msg': 'slider verify, refresh to click verify'}
        logger.info('img_url: %s' % url)
        headers = {
            'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        }
        res = get(url, headers=headers)
        if not res.get('is_success'):
            return {'succ': False, 'msg': 'net error'}
        img = res.get('msg').content
        with open(join(IMG_PATH, 'click_vc.png'), 'bw') as i:
            i.write(img)
        vc = u.rc.rk_create(img, 6906, timeout=90)
        del (img)
        # if not vc.get('Result'):
        #     u.rc.rk_report_error(vc.get('Id'))
        #     return self.get_vc_img()
        return {'succ': True, 'msg': vc}

    def gen_line_point(self, point):
        """
        生成轨迹线的坐标点
        :param point: 目标坐标点
        :return: 两个列表，x的列表和y的列表
        """
        # 生成中点偏移量
        p1 = u.pag.position()
        x = [p1[0], point[0]]
        y = [p1[1], point[1]]
        x_max, x_min = max(x), min(x)
        y_max, y_min = max(y), min(y)
        midx = random._ceil(random.uniform(x_min + 10, x_max - 10))
        midy = random._ceil(random.uniform(y_min + 10, y_max - 10))
        # mid_point = [random.randrange(x_min, x_max), random.randrange(y.min(), y.max())]
        if x_max - x_min <= 5:
            midx = x_max + 15

        # 生成轨迹线
        line_x = arange(x_min, x_max, 1)
        x.append(midx)
        y.append(midy)
        x.sort(), y.sort()
        x, y = array(x), array(y)
        line_func = interp1d(x, y, kind='quadratic')
        line_y = line_func(line_x)
        if p1[0] > point[0]:
            line_x = line_x[::-1]
            line_y = line_y[::-1]
        return line_x, line_y

    def get_point_location(self, ox, list_y, oAngle):
        """获取oAngle倾斜度的增量坐标
        :param ox: 当前x坐标
        :param list_y: 当前y总坐标
        """
        oy = 0
        for e in list_y:
            oy += e  # rel y
        try:
            radion = math.atan(list_y[-1] / ox)  # 弧度
            angle = math.degrees(radion)
            angle = angle if oy > 0 or oy == 0 else -angle
            l = math.sqrt(ox ** 2 + oy ** 2)
            x = l * math.cos(math.radians(angle + oAngle))
            y = l * math.sin(math.radians(angle + oAngle))
            return x, y
        except Exception as e:
            logger.error(e)

    def move_from_lines(self, dst_location):
        """v1: 手动录制的轨迹线，按增量滑动
        :param dst_location: (x, y)
        """
        x, y = u.pag.position()
        pos_list = random.choice(slides)  # 选择一条轨迹线
        list_y = []  # 已走过的Y的增量的和的值
        # 当前点与目标点之间的角度
        aby, abx = abs(y - dst_location[1]), abs(dst_location[0] - x)
        angle = math.degrees(math.atan(aby / abx))
        if abx > 0 and aby < 0:
            angle = -angle
        elif abx < 0 and aby < 0:
            angle = angle - 180
        elif abx < 0 and aby > 0:
            angle = 180 - angle
        for px, py, slpt in pos_list:  # 按增量滑动滑块
            if px == 0:
                time.sleep(slpt / 1000)
                continue
            list_y.append(py)
            nx, ny = self.get_point_location(px, list_y, angle)
            # u.pag.moveRel(nx, ny)
            mouse_move(int(x + nx), int(y + ny))
            x += nx
            y += ny
            if x > dst_location[0]:
                break
            time.sleep(slpt / 1000)
        return True

    def deal_vc(self, retrytimes, retries=1):
        # 获取图片验证码
        verify_code = self.get_vc_img()
        if not verify_code.get('succ'):
            return self.login(retrytimes)
        logger.info('text location: %s' % verify_code.get('msg').get('Result'))
        point = verify_code.get('msg').get('Result').split('.')

        # 点击验证
        relEle = self.d.find_element_by_class_name('geetest_item_img')
        chrome_title_height = 110  # 浏览器头部高度110;       # 缩放比例::  x: -11, y: -11
        x = relEle.location.get('x') - 11  # 页面图片相对坐标
        y = relEle.location.get('y') - 11 + chrome_title_height
        for p in point:
            pe = p.split(',')
            # sleep_time = round(random.uniform(0.5, 1), 2)
            location = (x + int(pe[0]), y + int(pe[1]))  # 汉字点的真实坐标
            """
            # v1: 生成补间点坐标
            line_x, line_y = self.gen_line_point(location)
            for e in range(len(line_x)):
                st = random.choice([0.001, 0.002, 0.003])
                # u.pag.moveTo(line_x[e], line_y[e], duration=st, tween=u.pag.easeOutQuad)
                mouse_move(int(line_x[e]), int(line_y[e]))
                time.sleep(st)
            """
            # v3: 利用收录的轨迹线移动
            self.move_from_lines(location)
            if u.pag.position() != location:
                u.pag.click(location[0], location[1], duration=0.5, tween=u.pag.easeOutQuad)
            else:
                u.pag.click(location[0], location[1], duration=0.1)
            # v2: 利用selenium自带的actionChain类来完成图的点击操作
            # vc_img = self.d.find_element_by_class_name('geetest_item_img')
            # self.act.move_to_element_with_offset(vc_img, pe[0], pe[1]).click().perform()
            # time.sleep(sleep_time)

        self.d.find_element_by_class_name('geetest_commit').click()  # 点击确认
        """
        cx = gt_commit.location.get('x')
        cy = gt_commit.location.get('y')
        line_x, line_y = self.gen_line_point((int(cx), int(cy)))
        for e in range(len(line_x)):
            mouse_move(int(line_x[e]), int(line_y[e]))
            time.sleep(0.001)
        """
        # self.slip_to_dst(gt_commit)
        time.sleep(2)

        vc_res = self.d.find_element_by_class_name('geetest_success_radar_tip_content').text  # 判断点击验证结果
        if vc_res != '验证成功':
            if retries == 3:
                return self.login(retrytimes)
            retries += 1
            self.d.find_element_by_class_name('geetest_refresh').click()
            time.sleep(1)
            return self.deal_vc(retrytimes, retries=retries)
        # 点击登陆并判断结果
        self.d.find_element_by_id('login').click()
        time.sleep(2)
        # res = self.is_login(check_cookie)
        try:
            self.d.find_element_by_id('head-logout')
            return {'succ': True, 'msg': 'login success'}
        except:
            logger.info('no logout btn, mean not login, pass to vc_pwd step')
            return {'succ': False, 'msg': 'pd'}

    def slip_to_dst(self, element):
        # stx, sty = u.pag.size()
        # u.pag.moveTo(int(stx/2), int(sty/2))
        x, y = element.location.get('x'), element.location.get('y') + 110
        u.pag.moveTo(x, y, duration=0.3)

    def login(self, retrytimes=0):
        url = 'https://e.meizu.com'
        try:
            self.get(url)
            # self.d.find_element_by_link_text('登录')
            self.d.execute_script("document.querySelectorAll('.home-wrapper a')[5].click()")
            time.sleep(2)
            account = self.d.find_element_by_id('account')
            account.clear()
            account.send_keys(self.acc)
            time.sleep(1)

            password = self.d.find_element_by_id('password')
            password.clear()
            password.send_keys(self.pwd)
            time.sleep(1)

            logger.info('acc_info------acc: %s~~~~pwd: %s' % (self.acc, self.pwd))
            ir = input('请输入账号情况对应数字（1：正常  2：异常,然后重试！ 3: 异常，跳过且不重试！ 其他：重新开始）>>\n')
            if ir == '1':
                self.d.get('http://e.meizu.com/views/home.html')  # 强制跳转到旧页面
                time.sleep(2)
                cookies = self.d.get_cookies()
                return {'succ': True, 'cookies': cookies, 'driver': self.d}
            elif ir == '2':
                er = input('请输入异常描述(验证码多次错误则直接输入: vc)，然后回车结束>>\n')
                if retrytimes == 5:
                    return {'succ': False, 'msg': er}
                logger.info('retry times: %s' % retrytimes)
                retrytimes += 1
                return self.login(retrytimes=retrytimes)
            elif ir == '3':
                er = input('请输入异常描述，然后回车结束>>\n')
                return {'succ': False, 'msg': er}
            else:
                return self.login(retrytimes=retrytimes)

            # self.d.find_element_by_class_name('geetest_radar_tip').click()      # 点开验证码
            #
            # 查看是否需要验证码
            # try:
            #     time.sleep(3)
            #     res = self.d.find_element_by_class_name('geetest_success_radar_tip_content').text
            #     if res == '验证成功':
            #         cookies = self.d.get_cookies()
            #         return {'succ': True, 'cookies': cookies, 'driver': self.d}
            # except:
            #     logger.debug('需要验证码，进入验证环节')

            # time.sleep(1)
            # 处理验证码和判断登陆结果
            # login_res = self.deal_vc(retrytimes)
            # if not login_res.get('succ') and login_res.get('msg') == 'pd':
            #     if retrytimes == 5:
            #         return login_res
            #     retrytimes += 1
            #     time.sleep(2)
            #     return self.login(retrytimes=retrytimes)
        except Exception as e:
            logger.error(e, exc_info=1)
            if retrytimes == 5:
                return {'succ': False, 'msg': e}
            retrytimes += 1
            return self.login(retrytimes=retrytimes)

    def run_login(self):
        self.d = self.init_driver()
        res = self.login()

        if not res.get('succ'):
            # params = [self.user_info.get('id'), self.acc, self.user_info.get('platform'), None, False]
            self.d.quit()
            # if not post_res(*params):
            #     logger.error('login failed, post failed, account: %s' % self.acc)
            #     return res
            logger.info('login failed, Ready to post res')
            res['invalid_account'] = True
        return res
