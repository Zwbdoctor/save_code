import time
import random
import os
from logging import getLogger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains


from lib.utils import Util
from lib.post_get import get

logger = None
vc_path = os.path.join('\\'.join(__file__.split('\\')[:-2]), 'data', 'verifyCode.png')

slides = [
    [[2,1,16],[2,0,14],[3,0,2],[3,0,9],[3,1,8],[4,0,9],[4,0,8],[5,0,9],[6,0,5],[8,0,12],[6,0,6],[8,0,10],[22,0,25],[5,0,10],[5,0,2],[4,0,7],[3,0,13],[3,0,4],[4,0,16],[4,0,15],[3,0,1],[4,0,12],[3,0,3],[4,0,11],[2,0,5],[3,0,13],[3,0,3],[3,0,14],[1,0,3],[5,2,15],[3,0,17],[6,0,17],[5,0,15],[6,0,15],[2,0,16],[2,0,3],[1,0,6],[2,0,9],[1,0,7],[3,0,10],[1,0,6],[2,0,10],[1,0,6],[2,0,8],[2,0,8],[1,0,8],[1,0,8],[1,0,9],[2,0,8],[1,1,15],[1,0,16],[1,0,14],[1,0,2],[1,0,13],[1,0,3],[1,0,13],[2,0,3],[1,0,16],[1,0,101],[1,0,50],[1,1,16],[1,0,233],[1,0,23],[1,1,127],[1,0,167],[1,0,349]],
    [[0,0,85],[1,0,55],[1,0,12],[1,0,19],[3,0,16],[5,0,17],[3,0,16],[5,0,17],[5,0,17],[5,1,17],[6,0,18],[5,0,17],[6,0,16],[14,1,18],[9,1,16],[6,0,17],[5,0,18],[5,0,16],[5,0,17],[4,0,17],[4,0,18],[4,0,16],[5,0,17],[2,0,17],[5,0,18],[4,0,17],[4,-1,15],[5,0,18],[3,0,17],[5,-1,17],[4,0,17],[6,0,17],[3,0,16],[3,-1,17],[3,0,17],[2,0,17],[5,-1,19],[4,0,14],[5,0,18],[6,-1,17],[4,-1,17],[2,0,17],[4,-1,17],[3,0,17],[1,0,17],[1,0,27],[2,0,24],[1,0,17],[2,0,18],[1,0,15],[0,0,131],[-1,0,175],[-1,0,92],[-1,0,79],[0,0,174],[-1,0,27]],
    [[3,0,16],[4,0,20],[5,0,13],[4,-1,17],[5,0,17],[4,-1,17],[5,0,17],[9,0,18],[7,0,17],[6,0,17],[7,0,17],[6,0,16],[6,0,17],[6,0,17],[6,0,17],[11,0,17],[7,0,18],[6,0,16],[6,0,17],[6,0,17],[5,0,18],[5,0,16],[4,0,18],[7,0,17],[3,0,16],[3,0,16],[3,0,19],[4,0,16],[2,0,16],[4,0,17],[3,0,17],[2,-1,16],[3,0,17],[3,0,18],[2,0,16],[1,0,17],[1,0,47],[1,-1,30],[1,0,72],[1,0,22],[1,0,43],[1,0,31],[1,0,24],[1,0,20],[1,0,69],[1,0,16],[1,0,16],[1,0,17],[1,0,17]],
    [[3,0,20],[6,0,18],[11,0,16],[14,2,16],[23,2,17],[12,1,17],[10,0,17],[7,0,19],[5,0,15],[5,0,17],[6,0,17],[6,0,17],[9,0,17],[6,0,17],[7,0,17],[5,0,18],[7,0,17],[8,0,16],[9,0,18],[6,0,16],[7,0,17],[1,0,16],[2,0,18],[5,0,16],[7,0,17],[6,0,17],[5,0,17],[1,0,17],[-1,0,204],[-1,0,19],[-1,0,15]],
    [[5,0,17],[9,0,17],[8,0,17],[7,0,16],[6,0,17],[7,0,18],[6,0,16],[6,-1,17],[10,0,17],[7,-1,18],[6,0,17],[5,0,15],[6,-1,18],[6,-1,18],[6,0,16],[8,-1,17],[4,0,17],[5,0,16],[4,0,18],[4,0,17],[5,0,16],[4,0,18],[5,0,18],[3,0,16],[5,0,17],[3,0,16],[2,0,19],[3,0,16],[2,0,17],[2,0,15],[1,0,20],[1,0,17],[2,0,15],[1,0,73],[1,0,28],[1,0,17],[1,0,17],[1,0,17],[1,0,17],[1,0,17],[1,0,17],[2,0,17],[2,0,17],[1,0,16],[1,0,84],[1,0,304],[1,0,31],[1,0,32]],
    [[1,0,33],[1,0,18],[1,0,15],[2,0,16],[3,0,17],[6,0,18],[5,0,16],[6,0,17],[7,0,16],[7,1,18],[9,1,17],[5,0,16],[5,0,18],[6,0,17],[4,0,17],[3,0,18],[5,0,16],[7,0,17],[6,0,17],[5,0,17],[4,0,16],[5,0,18],[3,1,16],[4,0,17],[7,0,17],[5,0,17],[8,0,17],[6,0,18],[7,1,17],[6,0,18],[5,0,16],[4,0,16],[5,0,17],[2,0,17],[4,0,18],[3,0,16],[2,0,18],[2,0,16],[1,0,19],[1,0,14],[1,0,18],[1,0,17],[1,0,210],[2,0,27],[1,0,17],[1,0,18],[1,0,16],[1,0,17],[-1,0,377],[-1,0,16],[-1,0,23],[-1,0,24],[0,1,119],[1,0,17],[1,0,129]],
    [[1,0,50],[1,0,17],[1,0,17],[1,0,17],[2,0,17],[5,0,17],[8,0,16],[11,0,17],[12,0,18],[15,0,16],[18,0,18],[10,0,17],[8,0,17],[7,-1,17],[5,0,17],[6,0,17],[4,0,17],[6,0,17],[7,0,17],[5,-1,16],[3,0,17],[3,0,17],[2,0,17],[1,0,16],[1,-1,18],[2,0,17],[1,0,17],[2,0,17],[1,0,17],[2,0,17],[1,0,17],[2,0,17],[1,0,17],[1,0,18],[1,0,16],[1,0,49],[1,0,23],[1,0,25],[1,0,21],[1,0,27],[1,0,24],[1,0,17],[1,0,23],[1,0,16],[1,0,17],[1,0,15],[1,0,56],[1,0,56],[1,0,24],[1,0,209],[1,0,31],[1,1,96],[1,0,40]],
    [[1,0,43],[1,0,18],[1,0,17],[3,0,17],[5,0,17],[9,0,17],[9,0,17],[8,0,16],[8,0,18],[10,0,16],[11,0,18],[11,0,17],[10,0,17],[11,0,16],[7,0,18],[6,0,17],[6,0,17],[6,0,17],[5,0,16],[4,0,17],[6,0,16],[8,0,18],[16,0,17],[8,0,16],[5,0,18],[2,-1,17],[1,0,221],[1,0,104],[1,0,15],[1,0,18],[1,0,15],[1,0,127],[1,0,361]],
    [[2,0,29],[5,0,16],[6,0,18],[6,0,18],[15,0,16],[12,1,17],[9,0,17],[8,0,16],[6,0,17],[6,0,17],[6,0,18],[6,-1,17],[10,-2,17],[6,0,16],[5,-1,17],[4,0,18],[2,0,17],[3,0,16],[3,0,18],[4,0,17],[7,0,17],[4,0,15],[3,0,18],[4,0,16],[3,0,18],[4,0,17],[4,0,17],[4,0,17],[2,0,16],[4,0,18],[3,0,17],[3,0,16],[2,0,17],[3,0,18],[1,0,16],[1,0,17],[1,0,17],[1,0,18],[2,0,16],[2,0,18],[2,0,17],[1,0,17],[1,0,85]],
    [[1,0,15],[5,0,16],[10,0,16],[14,0,18],[18,0,17],[15,0,16],[13,0,17],[17,0,23],[6,-1,12],[14,0,16],[8,0,17],[8,-1,18],[4,-1,17],[3,0,16],[1,0,18],[1,0,17],[1,-1,16],[2,0,18],[0,-1,17],[1,0,18],[1,0,33],[1,0,16],[1,0,18],[1,-1,17],[1,0,16],[2,0,17],[3,0,17],[4,-1,16],[2,0,18],[3,0,17],[2,0,68],[1,0,17],[2,0,16],[1,0,17],[1,0,17],[1,0,67],[1,0,33],[1,0,19],[2,0,33],[1,0,86],[1,0,272],[1,0,155]],
    [[1,0,23],[1,0,16],[1,0,16],[7,0,17],[6,0,17],[8,0,17],[9,0,18],[10,0,17],[9,0,16],[9,0,17],[7,0,17],[13,-2,16],[9,-1,19],[7,0,16],[7,-1,17],[5,0,16],[6,0,18],[5,0,16],[5,0,20],[8,0,16],[4,-1,17],[5,0,17],[3,0,16],[4,0,18],[4,0,17],[4,0,16],[6,0,17],[5,0,17],[2,0,17],[1,0,18],[0,-1,16],[1,0,17],[1,0,17],[1,0,16],[1,0,17],[1,0,68],[1,0,34],[0,-1,34],[1,0,17],[1,0,17],[1,0,35],[1,0,17],[1,0,34],[1,0,34],[1,0,17],[1,0,32],[1,0,101],[1,0,86],[1,0,18],[1,0,68],[1,0,31]]
]


class LoginQQ:

    def __init__(self, user_info, logger_name):
        global logger
        self.d = None
        self.u = Util()
        self.user_info = user_info
        self.line_path = None
        self.act = None
        logger = getLogger(logger_name)

    def init_driver(self):
        op = Options()
        op.add_argument('--disable-gpu')
        op.add_argument('--headless')
        op.add_argument('window-size=1920x1080')  # 指定浏览器分辨率
        driver = webdriver.Chrome(chrome_options=op)
        self.act = ActionChains(driver)
        # driver = webdriver.Chrome()
        driver.set_page_load_timeout(60)
        driver.set_script_timeout(30)
        driver.maximize_window()
        return driver

    def get(self, url):
        try:
            self.d.delete_all_cookies()
            self.d.get(url)
        except: # 超时重试一次
            self.d.delete_all_cookies()
            self.d.get(url)
        time.sleep(3)

    def getGTK(self, skey):
        hashes = 5381
        for letter in skey:
            hashes += (hashes << 5) + ord(letter)
        return hashes & 0x7fffffff

    def wait_element(self, ele_type, element, wait_time=20, ec=EC.presence_of_element_located):
        ele = WebDriverWait(self.d, wait_time).until(ec((ele_type, element)))
        return ele

    def wait_vc(self, wait_sth, wt):        # 等待验证码出现
        try:
            self.d.switch_to.frame(self.d.find_element_by_xpath('//*[@id="newVcodeIframe"]/iframe'))
            WebDriverWait(self.d, wt, 0.5).until(
                EC.presence_of_element_located(wait_sth))
            return True
        except:
            return False

    def slip_vc_box(self, dst_location, box_location, btn_height):
        """v1: 手动录制的轨迹线，按增量滑动"""
        element = self.d.find_element_by_id('tcaptcha_drag_button')
        left = element.location['x'] + box_location[0]
        # top = element.location['y'] + box_loation[1]
        x = int(left + int(element.size['width']/2))
        y = btn_height
        # self.u.pag.mouseDown(x, y)
        distance = dst_location[0] - x        # 第二段len(x)
        act = ActionChains(self.d)
        act.click_and_hold(element).perform()
        tracks = self.get_tracks(distance/5, 3)
        # with open(self.line_path, 'br') as l:
        #     pos_list = pickle.load(l)           # 读取轨迹线坐标（坐标增量）
        # pos_list = random.choice(slides)    # 选择一条轨迹线
        # for px, py, slpt in pos_list:       # 按增量滑动滑块
        for px, py, slpt in tracks:       # 按增量滑动滑块
            # self.u.pag.moveRel(px, py)
            print([px, py, slpt])
            act.move_by_offset(1, py/2).perform()
            x = px*6 + x
            y = py*6 + y
            # print([x, y, dst_location[0]])
            if x > dst_location[0]:
                break
            # time.sleep(slpt/1000)
            time.sleep(0.0001)
        act.release(element).perform()
        # else:
        #     self.u.pag.moveTo(dst_location[0]+10, y)
        #     self.u.pag.mouseUp(dst_location[0], y)
        # self.u.pag.mouseUp(dst_location[0]+10, y)
        time.sleep(5)
        logger.info('slip vc_block ok')

    def get_tracks(self, distance, dist_y):
        '''
        拿到移动轨迹，模仿人的滑动行为，先匀加速后匀减速
        匀变速运动基本公式：
        ①v=v0+at
        ②s=v0t+½at²
        ③v²-v0²=2as
        :param distance: 需要移动的距离
        :return: 存放每0.3秒移动的距离
        '''
        # 初速度
        v = 0
        vy = 0
        # 单位时间为0.2s来统计轨迹，轨迹即0.2内的位移
        t = 0.3
        # 位移/轨迹列表，列表内的一个元素代表0.2s的位移
        tracks = []
        # 当前的位移
        current = 0
        currenty = 0
        # 到达mid值开始减速
        rand_mid = random.choice([3, 4])
        mid = distance * rand_mid / 5
        midy = 3 if rand_mid == 4 else 4
        midy = dist_y * midy

        while current < distance:
            if current < mid:
                # 加速度越小，单位时间的位移越小,模拟的轨迹就越多越详细
                a = 2
            else:
                a = -3

            ay = 1.5 if currenty < midy else -3.5

            # 初速度
            v0 = v
            y0 = vy
            # 0.2秒时间内的位移
            s = v0 * t + 0.5 * a * (t ** 2)
            sy = y0 * t + 0.5 * ay * (t ** 2)
            # 当前的位置
            current += s
            currenty += sy
            # 添加到轨迹列表
            tracks.append([round(s), round(sy), t])

            # 速度已经达到v,该速度作为下次的初速度
            v = v0 + a * t
            vy = y0 + ay * t
        return tracks

    def slip_vc_box_v2(self, dst_location, box_location, btn_height):
        """
        v2: 利用pyautogui, 根据坐标生成两段轨迹线，增量移动滑块
            dst_location缺口坐标，box_location滑块坐标，btn_height
        """
        element = self.d.find_element_by_id('tcaptcha_drag_button')
        left = element.location['x'] + box_location[0]
        # 初始化起始位置
        x = int(left + int(element.size['width']/2))
        y = btn_height

        self.u.pag.mouseDown(x, y)
        # act = ActionChains(self.d)
        # act.click_and_hold(element)
        half_x = random.randrange(90, 130)      # 第一段len(x)
        yl = [5, 6, 7, -4, -5, -6]              # y 上下浮动
        last_len = dst_location[0] - x - half_x + 10        # 第二段len(x)
        speed = self.u.pag.easeInOutQuad   # 开始和最后快速，中间慢速
        point = [(half_x, random.choice(yl), round(random.uniform(1.5, 2.5), 2), speed)]            # 第一段
        point.append((last_len, random.choice(yl), round(random.uniform(1.5, 2.5), 2), speed))      # 最后一段
        for xl, y, t, tween_method in point:
            self.u.pag.moveRel(xl, y, t, tween=tween_method)
        self.u.pag.mouseUp(dst_location[0], y)
        time.sleep(5)
        logger.info('slip vc_block ok')

    def deal_vc(self, abs_x, abs_y, btn_height):
        # vc_method = [self.slip_vc_box.slip_vc_box_v2]
        """等待3秒，判断是否出现滑块验证码，出现即执行验证操作, 完成以后判断是否登陆成功"""
        wait_sth = (By.ID, 'slideBkg')
        if self.wait_vc(wait_sth, 3):      # 出现验证码
            # time.sleep(2)
            logger.info('Please slip the verify box by your hand ....')
            self.d.implicitly_wait(10)
            WebDriverWait(self.d, 30).until_not(EC.visibility_of_element_located((By.ID, 'loginBtn')))
        # """
            element = self.d.find_element_by_id('slideBkg')
            self.u.cutimg_by_driver(self.d, element, vc_path, abx=abs_x, aby=abs_y)  # 裁剪
            with open(vc_path, 'br') as i:
                im = i.read()
            for e in range(2):
                lt = self.u.rc.rk_create(im, '6137').get('Result')  # 获取验证码坐标 2次容错(坐标获取)
                if lt:
                    location = lt.split(',')
                    lt = [int(location[0]) + abs_x, int(location[1]) + abs_y]
                    # 随机选择一个滑动方法
                    # slip_method = random.choice(vc_method)
                    # slip_method(lt, [abs_x, abs_y], btn_height)    # 执行滑动操作
                    self.slip_vc_box(lt, [abs_x, abs_y], btn_height)    # 执行滑动操作
                    logger.info('vc_block location: ')
                    logger.info(lt)
                    break
            else:
                logger.error('----------get vc_location failed')
                return {'succ': False, 'msg': 'get vc_location failed after 2 times'}
        # v1: 登陆结果验证
        try:
            # 仍然在验证码界面则验证码错误, 否则密码错误
            self.d.switch_to_default_content()
            self.d.switch_to.frame('ui_ptlogin')
            try:
                self.d.switch_to.frame(self.d.find_element_by_xpath('//*[@id="newVcodeIframe"]/iframe'))
                return {'succ': False, 'msg': 'vc'}
            except:
                return {'succ': False, 'msg': 'pd'}
        except Exception as e:
            logger.info('login succ, jump this step')        # 没有进入小窗口，则登陆成功
        # """
        # v2: 登陆结果验证
        # time.sleep(10)
        time.sleep(1)
        return self.is_login()

    def is_login(self):     # 判断cookie中是否存在skey,这个是login成功时response set-cookie
        time.sleep(3)
        cks = self.d.get_cookies()
        isCksContainSkey = False
        for ck in cks:
            if ck['name'] == 'gdt_protect':
                isCksContainSkey = True
        if isCksContainSkey:
            return {'succ': True, 'msg':'login success', 'cookies':cks}
        else:
            return {'succ': False, 'msg':'login failed'}

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
        try:        # 另一个不同版本的开始引导界面
            for e in range(2):
                self.wait_element(By.LINK_TEXT, '我知道了', wait_time=3).click()
                time.sleep(1)
            else:
                self.wait_element(By.LINK_TEXT, '广告投放').click()
                time.sleep(2)
                handles = self.d.window_handles
                self.d.switch_to.window(handles[-1])
        except:
            logger.info('跳过另一个版本的引导界面')

    def get_uid_another_version(self):
        url = 'https://e.qq.com/gaea/api.php'
        cookie = self.d.get_cookies()
        cookie = {e['name']: e['value'] for e in cookie}
        skey = cookie.get('skey') if not cookie.get('gdt_protect') else cookie.get('gdt_protect')
        g_tk = self.getGTK(skey)
        params = {'mod': 'report', 'act': 'customer', 'g_tk': g_tk}
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

    def get_into(self, reties=1):
        """跳转至管理页面,获取cookies"""
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
            with open(os.path.join(os.path.dirname(__file__), 'e_qq_delete_mask.js'), 'r') as f:
                js = f.read()
            self.d.execute_script(js)
            time.sleep(3)
            self.wait_element(By.TAG_NAME, 'table', wait_time=5)
            # 用户uid
            cks = self.d.get_cookies()
            return {'succ': True, 'cookie': cks, 'driver': self.d}
        except Exception as e:
            logger.warning(e, exc_info=1)
            reties += 1
            if reties == 3:
                return {'succ': True, 'msg': "login success, but can not get into manage page"}
            return self.get_into(reties=reties)

    def login(self):
        url = 'https://e.qq.com/ads/'
        self.get(url)
        try:
            # self.d.implicitly_wait(30)
            self.wait_element(By.ID, 'loginBtn', ec=EC.element_to_be_clickable).click()
            try:
                abx = self.d.find_element_by_id('ui_ptlogin').location['x']
                aby = self.d.find_element_by_id('ui_ptlogin').location['y']
                time.sleep(1)
                self.d.switch_to.frame('ui_ptlogin')
            except:
                # logger.info('兼容另一版本的登陆界面')
                abx = self.d.find_element_by_id('ptlogin_iframe').location['x']
                aby = self.d.find_element_by_id('ptlogin_iframe').location['y']
                # abx = self.wait_element(By.ID, 'ptlogin_iframe').location['x']
                # aby = self.wait_element(By.ID, 'ptlogin_iframe').location['y']
                time.sleep(1)
                self.d.switch_to.frame('ptlogin_iframe')
            self.wait_element(By.ID, 'switcher_plogin').click()
            time.sleep(1)
            self.d.find_element_by_id('u').clear()
            self.d.find_element_by_id('u').send_keys(self.user_info['account'])
            time.sleep(0.5)
            self.d.find_element_by_id('p').send_keys(self.user_info['password'])
            time.sleep(1)
            self.d.find_element_by_id('login_button').click()
            time.sleep(3)

            try:
                # 等待是否出现验证码 并 判断是否登陆成功
                abs_x = self.d.find_element_by_id('newVcodeIframe').location['x'] + abx
                abs_y = self.d.find_element_by_id('newVcodeIframe').location['y'] + aby
                btn_height = abs_y + 306
                lres = self.deal_vc(abs_x, abs_y, btn_height)
                if lres.get('succ') and lres.get('ret') == 4000:
                    return lres
                elif not lres.get('succ'):
                    logger.warning('login failed msg:')
                    logger.error(lres)
                    return lres
            except NoSuchElementException:
                logger.info('no verify, pass step')
            except Exception as evc:
                logger.info(evc, exc_info=1)
            logger.info('login success')
            # logger.info('%s\t\tpwd:  %s' % (self.user_info['account'], self.user_info['password']))

            # 查看账户是否有其他异常
            erm = self.wait_element(By.ID, 'loginErrorMsg', wait_time=10).text
            login_btn_text = self.d.execute_script('return document.querySelector(".btn-login").text')
            if erm != '' and login_btn_text.strip() == '登录投放管理平台':
                return {'succ': True, 'msg': 'unknown situation', 'desc': erm}
        except Exception as e:
            logger.error(e, exc_info=1)
            self.d.close()
            return {'succ': False, 'msg': e}

        cks = self.d.get_cookies()
        self.d.quit()
        return {'succ': True, 'cookie': cks}

    def run_login(self):
        res = None
        for e in range(3):            
            self.d = self.init_driver()
            res = self.login()
            if res['succ']:
                return res
            else:
                self.d.quit()
        else:
            # 上报无效
            logger.error('----------Useless account! Please check your account or password and try again!')
            self.d.quit()
            return {'succ': False, 'msg': res.get('msg')}

