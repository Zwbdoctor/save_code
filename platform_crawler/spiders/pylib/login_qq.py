import time
import random
import os
from logging import getLogger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from platform_crawler.utils.utils import Util
from platform_crawler.utils.post_get import get
from platform_crawler.spiders.pylib.login_qq_with_cli import login_cli, kill_qq
from platform_crawler.spiders.pylib.slip_py import vc_location
from platform_crawler.settings import join, JS_PATH, IMG_PATH, GlobalFunc, GlobalVal

logger = None
base_vc_path = join(IMG_PATH, 'slip_vc_imgs')
if not os.path.exists(base_vc_path):
    os.makedirs(base_vc_path)
bg_name = join(base_vc_path, 'bg.jpg')
box_name = join(base_vc_path, 'box.png')

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


class LoginQQ:

    def __init__(self, user_info, logger_name):
        global logger
        self.d = None
        self.u = Util()
        self.user_info = user_info
        self.line_path = None
        self.cookies = {}
        self.gtk = None
        logger = getLogger(logger_name)

    def init_driver(self):
        driver = webdriver.Chrome()
        driver.set_page_load_timeout(60)
        driver.set_script_timeout(30)
        driver.maximize_window()
        return driver

    def get(self, url):
        try:
            self.d.delete_all_cookies()
            self.d.get(url)
        except:  # 超时重试一次
            self.d.delete_all_cookies()
            self.d.get(url)
        self.d.implicitly_wait(3)
        time.sleep(3)

    def getGTK(self, skey):
        hashes = 5381
        for letter in skey:
            hashes += (hashes << 5) + ord(letter)
        return hashes & 0x7fffffff

    def wait_element(self, ele_type, element, wait_time=20, ec=EC.presence_of_element_located):
        ele = WebDriverWait(self.d, wait_time).until(ec((ele_type, element)))
        return ele

    def wait_vc(self):  # 等待验证码出现
        try:
            self.d.switch_to.frame(self.d.find_element_by_xpath('//*[@id="newVcodeIframe"]/iframe'))
            self.d.find_element_by_id('slideBgWrap')
            return True
        except:
            return False

    def slip_vc_box(self, dst_location, box_location, btn_height):
        """v1: 手动录制的轨迹线，按增量滑动"""
        element = self.d.find_element_by_id('tcaptcha_drag_thumb')
        left = element.location['x'] + box_location[0]
        # top = element.location['y'] + box_loation[1]
        x = int(left + int(element.size['width'] / 2))
        y = btn_height
        self.u.pag.mouseDown(x, y)
        # with open(self.line_path, 'br') as l:
        #     pos_list = pickle.load(l)           # 读取轨迹线坐标（坐标增量）
        pos_list = random.choice(slides)  # 选择一条轨迹线
        for px, py, slpt in pos_list:  # 按增量滑动滑块
            self.u.pag.moveRel(px, py)
            x += px
            y += py
            if x > dst_location[0] + 10:
                break
            time.sleep(slpt / 1000)
        else:
            self.u.pag.moveTo(dst_location[0] + 10, y)
            self.u.pag.mouseUp(dst_location[0], y)
        self.u.pag.mouseUp(dst_location[0] + 10, y)
        time.sleep(5)
        logger.info('slip vc_block ok')

    def slip_vc_box_v2(self, dst_location, box_location, btn_height):
        """
        v2: 利用pyautogui, 根据坐标生成两段轨迹线，增量移动滑块
            dst_location缺口坐标，box_location滑块坐标，btn_height
        """
        element = self.d.find_element_by_id('tcaptcha_drag_button')
        left = element.location['x'] + box_location[0]
        # 初始化起始位置
        x = int(left + int(element.size['width'] / 2))
        y = btn_height

        self.u.pag.mouseDown(x, y)
        half_x = random.randrange(90, 130)  # 第一段len(x)
        yl = [5, 6, 7, -4, -5, -6]  # y 上下浮动
        last_len = dst_location[0] - x - half_x + 10  # 第二段len(x)
        speed = self.u.pag.easeInOutQuad  # 开始和最后快速，中间慢速
        point = [(half_x, random.choice(yl), round(random.uniform(1.5, 2.5), 2), speed)]        # 第一段
        point.append((last_len, random.choice(yl), round(random.uniform(1.5, 2.5), 2), speed))  # 最后一段
        for xl, y, t, tween_method in point:
            self.u.pag.moveRel(xl, y, t, tween=tween_method)
        self.u.pag.mouseUp(dst_location[0], y)
        time.sleep(5)
        logger.info('slip vc_block ok')

    def save_pic(self, src, pic_name):
        from requests import get
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36'
        }
        res = get(src, headers=headers)
        with open(pic_name, 'bw') as f:
            f.write(res.content)

    def deal_vc(self, abs_x, abs_y, btn_height):
        vc_method = [self.slip_vc_box, self.slip_vc_box_v2]
        """等待3秒，判断是否出现滑块验证码，出现即执行验证操作, 完成以后判断是否登陆成功"""
        time.sleep(1.5)
        self.d.implicitly_wait(20)
        if self.wait_vc():  # 出现验证码
            # time.sleep(2)
            bg_src = self.d.find_element_by_id('slideBg').get_attribute('src')  # 裁剪
            self.save_pic(bg_src, bg_name)
            box_src = self.d.find_element_by_id('slideBlock').get_attribute('src')
            self.save_pic(box_src, box_name)
            for e in range(2):
                # lt = self.u.rc.rk_create(im, '6137').get('Result')  # 获取验证码坐标 2次容错(坐标获取)
                location = vc_location(box_name, bg_name)
                if location:
                    lt = [int(location[0]) + abs_x, int(location[1]) + abs_y]
                    # 随机选择一个滑动方法
                    slip_method = random.choice(vc_method)
                    try:
                        slip_method(lt, [abs_x, abs_y], btn_height)  # 执行滑动操作
                    except Exception as ee:
                        logger.error(ee, exc_info=1)
                    finally:
                        self.u.pag.mouseUp()
                    logger.info('vc_block location: ')
                    logger.info(lt)
                    break
            else:
                logger.error('----------get vc_location failed')
                GlobalFunc.save_screen_shot(GlobalVal.err_src_name % int(time.time() * 1000))
                return {'succ': False, 'msg': 'get vc_location failed after 2 times'}
        self.d.implicitly_wait(20)
        time.sleep(2)
        # input('please login qq')
        res = self.is_login()
        if not res.get('succ'):
            if not login_cli(self.user_info.get('account'), self.user_info.get('password'), self.u):
                kill_qq(src=False)
                logger.error('something error about account or password')
                return {'succ': False, 'msg': 'acc_pwd'}
            self.d.refresh()
            self.d.implicitly_wait(5)
            self.d.switch_to.frame('ptlogin_iframe')
            self.d.find_element_by_css_selector('#qlogin_list .face').click()  # 点击已经登陆的qq登陆
            self.d.implicitly_wait(5)
            res = self.is_login()
        kill_qq(src=False)
        return res

    def is_login(self):  # 判断cookie中是否存在skey,这个是login成功时response set-cookie
        time.sleep(3)
        cks = self.d.get_cookies()
        isCksContainSkey = False
        for ck in cks:
            if ck['name'] == 'gdt_protect':
                isCksContainSkey = True
        if isCksContainSkey:
            return {'succ': True, 'msg': 'login success', 'cookies': cks}
        else:
            return {'succ': False, 'msg': 'login failed'}

    def get_uid(self):
        cookie = self.d.get_cookies()
        cookie = {e['name']: e['value'] for e in cookie}
        url = 'https://e.qq.com/ec/loginfo.php'
        skey = cookie.get('skey') if not cookie.get('gdt_protect') else cookie.get('gdt_protect')
        g_tk = self.getGTK(skey)
        params = {'g_tk': g_tk}
        cookie = '; '.join(['%s=%s' % (k, v) for k, v in cookie.items()])
        headers = {
            'accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
            'cookie': cookie,
            'referer': 'https://e.qq.com/ads/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3569.0 Safari/537.36'
        }
        res = get(url, params=params, headers=headers)
        if not res.get('is_success'):
            return {'succ': False, 'msg': res.get('msg')}
        res = res.get('msg').json()
        if res.get('ret') == 0:
            uid = res.get('data').get('aduid')
            return {'succ': True, 'msg': 'login success', 'uid': uid}
        else:
            return {'succ': False, 'msg': 'login failed', 'desc': res.get('msg')}

    def another_guid_page(self):
        self.d.get('https://e.qq.com/gaea/customer/index')
        self.d.implicitly_wait(10)
        self.d.implicitly_wait(1.5)
        try:  # 另一个不同版本的开始引导界面
            for e in range(2):
                self.d.find_element_by_link_text('我知道了').click()
        except:
            logger.info('跳过另一个版本的引导界面')
        self.d.find_element_by_link_text('广告投放').click()
        time.sleep(2)
        handles = self.d.window_handles
        self.d.switch_to.window(handles[-1])

    def get_uid_another_version(self):
        url = 'https://e.qq.com/gaea/api.php'
        cookie = self.d.get_cookies()
        cookie = {e['name']: e['value'] for e in cookie}
        skey = cookie.get('skey') if not cookie.get('gdt_protect') else cookie.get('gdt_protect')
        g_tk = self.getGTK(skey)
        params = {'mod': 'customer', 'act': 'getlist', 'g_tk': g_tk}
        cookie = '; '.join(['%s=%s' % (k, v) for k, v in cookie.items()])
        headers = {
            'accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
            'cookie': cookie,
            'referer': 'https://e.qq.com/ads/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3569.0 Safari/537.36'
        }
        res = get(url, params=params, headers=headers)
        if not res.get('is_success'):
            return {'succ': False, 'msg': res.get('msg')}
        res = res.get('msg').json()
        if res.get('ret') == 0:
            uid = res.get('data').get('list')[0].get('uid')
            return {'succ': True, 'msg': 'login success', 'uid': uid}
        else:
            return {'succ': False, 'msg': 'login failed', 'desc': res.get('msg')}

    def get_into(self, reties=1, uid=None):
        """跳转至管理页面,获取cookies"""
        if not uid:
            uid = self.get_uid()
            if not uid.get('succ'):
                return uid
        try:
            self.d.get('https://e.qq.com/atlas/%s/report/producttype' % uid.get('uid'))
            try:
                WebDriverWait(self.d, 2).until(EC.alert_is_present()).accept()
                uid = self.get_uid_another_version()
                self.d.get('https://e.qq.com/atlas/%s/report/producttype' % uid.get('uid'))
            except:
                pass
            with open(join(JS_PATH, 'e_qq_delete_mask.js'), 'r') as f:
                js = f.read()
            self.d.execute_script(js)
            time.sleep(3)
            self.wait_element(By.TAG_NAME, 'table', wait_time=5)
            # 用户uid
            return {'succ': True, 'data': {'uid': uid.get('uid'), 'cookie': self.cookies.get('cookie_list')}, 'driver': self.d}
        except:
            reties += 1
            if reties == 3:
                return {'succ': True, 'msg': "login success, but can not get into manage page"}
            return self.get_into(reties=reties)

    def login(self):
        url = 'https://e.qq.com/ads/'
        self.get(url)
        try:
            self.d.find_element_by_id('loginBtn').click()
            try:
                abx = self.d.find_element_by_id('ui_ptlogin').location['x']
                aby = self.d.find_element_by_id('ui_ptlogin').location['y']
                time.sleep(1)
                self.d.switch_to.frame('ui_ptlogin')
            except:
                logger.info('兼容另一版本的登陆界面')
                abx = self.d.find_element_by_id('ptlogin_iframe').location['x']
                aby = self.d.find_element_by_id('ptlogin_iframe').location['y']
                time.sleep(1)
                self.d.switch_to.frame('ptlogin_iframe')
            self.d.find_element_by_id('switcher_plogin').click()
            time.sleep(1)
            self.d.find_element_by_id('u').clear()
            self.d.find_element_by_id('u').send_keys(self.user_info['account'])
            time.sleep(0.5)
            self.d.find_element_by_id('p').send_keys(self.user_info['password'])
            time.sleep(1)
            self.d.find_element_by_id('login_button').click()
            time.sleep(3)
            try:
                # 计算新iframe定位坐标系
                abs_x = self.d.find_element_by_id('newVcodeIframe').location['x'] + abx
                abs_y = self.d.find_element_by_id('newVcodeIframe').location['y'] + aby
                btn_height = abs_y + 313
                lres = self.deal_vc(abs_x, abs_y, btn_height)  # 验证码处理以及受保护后使用TIM登陆
                if not lres.get('succ'):
                    if 'vc_location' in lres.get('msg'):
                        return {'succ': False, 'msg': 'vc_location'}
                    elif lres.get('msg') == 'acc_pwd':
                        return {'succ': False, 'msg': 'break'}
                    logger.error('login failed msg:%s' % lres)
                    return lres
            except Exception as evc:
                logger.info(evc, exc_info=1)
                logger.info('no verify, pass step')
            logger.info('account:  %s' % self.user_info['account'])
            # 查看账户是否有其他异常
            self.d.switch_to.default_content()
            return self.deal_res_after_login()
        except Exception as e:
            logger.error(e, exc_info=1)
            self.d.close()
            return {'succ': False, 'msg': e}

    def deal_res_after_login(self):
        # 查看账户是否有其他异常
        erm_1 = self.wait_element(By.ID, 'loginErrorMsg', wait_time=10).text
        er_msg = self.d.find_element_by_id("fillUserInfo").get_attribute('style')  # 特殊异常账号（:信息不完善）
        uid = {}
        # login_btn_text = self.d.execute_script('return document.querySelector(".btn-login").text')
        login_btn_text = self.d.execute_script('return a=document.querySelector("a#in-manage-btn").textContent')
        if erm_1 != '' or 'display: none' not in er_msg:
            self.d.quit()
            logger.warning(f'{erm_1}|完善账号信息')
            return {'succ': True, 'msg': 'unknown situation', 'desc': f'{erm_1}|完善账号信息'}
        elif login_btn_text.strip() == '进入服务商管理平台':
            self.another_guid_page()
            uid = self.get_uid_another_version()

        logger.info('login success')

        self.build_cookies()
        return self.get_into(uid=uid if uid.get('succ') else None)

    def build_cookies(self):
        # 获取 cookies
        self.cookies['cookie_list'] = self.d.get_cookies()
        cookie_dict = {e['name']: e['value'] for e in self.cookies.get('cookie_list')}
        self.cookies['cookie_str'] = '; '.join(['%s=%s' % (k, v) for k, v in cookie_dict.items()])
        skey = cookie_dict.get('skey') if not cookie_dict.get('gdt_protect') else cookie_dict.get('gdt_protect')
        self.gtk = self.getGTK(skey)

    def get_balance(self, uid):
        url = "https://e.qq.com/ec/api.php"
        querystring = {"act": "dashboard", "g_tk": self.gtk, "owner": uid, "advertiser_id": uid,
                       "mod": "account", "unicode": "1"}
        headers = {
            'accept': "application/json, text/javascript, */*; q=0.01",
            'cookie': self.cookies.get('cookie_str'),
            'referer': f"https://e.qq.com/atlas/{uid}/",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
            'Host': "e.qq.com",
        }
        res = get(url, params=querystring, headers=headers)
        if not res.get('is_success'):
            logger.error(res.get('msg'), exc_info=1)
        data = res.get('msg').json()
        if not data.get('ret') == 0:
            logger.error(data.get('msg'))
            return {'succ': False}
        accounts = data.get('data').get('accounts')
        return {'succ': True, 'msg': accounts}

    def login_by_hand(self):
        url = 'https://e.qq.com/ads/'
        self.get(url)
        self.d.find_element_by_id('loginBtn').click()
        logger.info('兼容另一版本的登陆界面')
        # self.d.switch_to.frame('ptlogin_iframe')
        # self.d.find_element_by_id('switcher_plogin').click()
        # time.sleep(1)
        # self.d.find_element_by_id('u').clear()
        # self.d.find_element_by_id('u').send_keys(self.user_info['account'])
        # time.sleep(0.5)
        # self.d.find_element_by_id('p').send_keys(self.user_info['password'])
        # time.sleep(1)
        # self.d.find_element_by_id('login_button').click()
        input('Please login by your own, then press enter to continue')
        return self.deal_res_after_login()

    def run_login(self):
        res = None
        for e in range(1, 6):
            self.d = self.init_driver()
            res = self.login()
            # res = self.login_by_hand()
            if res['succ']:
                return res
            elif not res.get('succ'):
                if res.get('msg') == 'vc_location':
                    raise Exception('line 152: get vc_location failed')
                if res.get('msg') == 'break':
                    self.d.quit()
                    return {'succ': False, 'msg': res.get('msg'), 'invalid_account': True}
            else:
                self.d.quit()
        else:
            logger.info('useless account!(%s) Post success!' % self.user_info.get('account'))
            self.d.quit()
            return {'succ': False, 'msg': res.get('msg'), 'invalid_account': True}
