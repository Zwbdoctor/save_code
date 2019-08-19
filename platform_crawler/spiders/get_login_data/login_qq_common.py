import time
import random
from logging import getLogger
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from platform_crawler.utils.utils import Util
from platform_crawler.spiders.pylib.login_qq_with_cli import login_cli, kill_qq
from platform_crawler import settings

logger = None
vc_path = settings.join(settings.IMG_PATH, 'app_imgs', 'verifyCode.png')
img_temp_path = settings.temp_path

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

'''
qq公共登录
'''


class LoginQQCommon:
    def __init__(self, user_info):
        global logger
        self.u = Util()
        self.user_info = user_info
        self.line_path = None
        logger = getLogger('%s.login_qq_common' % user_info.get('platform'))

    def get(self, url):
        try:
            self.d.delete_all_cookies()
            self.d.get(url)
        except:  # 超时重试一次
            self.d.delete_all_cookies()
            self.d.get(url)
        time.sleep(3)

    def getGTK(self, skey):
        hashes = 5381
        for letter in skey:
            hashes += (hashes << 5) + ord(letter)
        return hashes & 0x7fffffff

    def slip_vc_box(self, dst_location, box_location, btn_height):
        """v1: 手动录制的轨迹线，按增量滑动"""
        element = self.d.find_element_by_id('tcaptcha_drag_button')
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
        point = [(half_x, random.choice(yl), round(random.uniform(1.5, 2.5), 2), speed)]  # 第一段
        point.append((last_len, random.choice(yl), round(random.uniform(1.5, 2.5), 2), speed))  # 最后一段
        for xl, y, t, tween_method in point:
            self.u.pag.moveRel(xl, y, t, tween=tween_method)
        self.u.pag.mouseUp(dst_location[0], y)
        time.sleep(5)
        logger.info('slip vc_block ok')

    def tim_login_process(self):
        res = self.is_login()
        if not res.get('succ'):
            # msg = self.d.execute_script("return document.querySelector('#err_m').textContent")
            if not login_cli(self.user_info.get('account'), self.user_info.get('password'), self.u):
                return {'succ': False, 'msg': 'something error about account or password'}
            self.d.refresh()
            self.d.implicitly_wait(5)
            self.d.find_element_by_id('header_login').click()   # 重新进入登录框
            time.sleep(1)
            login_iframe = self.d.find_element_by_css_selector('iframe[id="ui.ptlogin"]')
            self.d.switch_to.frame(login_iframe)
            self.d.find_element_by_css_selector('#qlogin_list .face').click()        # 点击已经登陆的qq登陆
            self.d.implicitly_wait(5)
            res = self.is_login()
            kill_qq()
        return res

    def deal_vc(self, abs_x, abs_y, btn_height):
        vc_method = [self.slip_vc_box, self.slip_vc_box_v2]
        element = WebDriverWait(self.d, 10).until(EC.visibility_of_element_located((By.ID, 'slideBg')))
        self.u.cutimg_by_driver(self.d, element, vc_path, abx=abs_x, aby=abs_y)  # 裁剪
        with open(vc_path, 'br') as i:
            im = i.read()
        for e in range(2):
            lt = self.u.rc.rk_create(im, '6137').get('Result')  # 获取验证码坐标 2次容错(坐标获取)
            if lt:
                location = lt.split(',')
                lt = [int(location[0]) + abs_x, int(location[1]) + abs_y]
                # 随机选择一个滑动方法
                slip_method = random.choice(vc_method)
                slip_method(lt, [abs_x, abs_y], btn_height)  # 执行滑动操作
                logger.info('vc_block location: ')
                logger.info(lt)
                break
        else:
            logger.error('----------get vc_location failed')
            return {'succ': False, 'msg': 'get vc_location failed after 2 times'}
        return self.tim_login_process()

    def is_login(self):  # 判断cookie中是否存在skey,这个是login成功时response set-cookie
        time.sleep(3)
        cks = self.d.get_cookies()
        isCksContainSkey = False
        for ck in cks:
            if ck['name'] == 'skey':
                isCksContainSkey = True
        if isCksContainSkey:
            return {'succ': True, 'msg': 'login success', 'cookies': cks}
        else:
            return {'succ': False, 'msg': 'login failed'}

    # 重试时会quit掉浏览器，所以driver会更新；不放在构造函数中，放到login方法中传递进来
    def login(self, driver, loginIfr, retrytimes=0):
        self.d = driver
        try:
            abx = loginIfr.location['x']
            aby = loginIfr.location['y']
            time.sleep(1)
            self.d.switch_to.frame(loginIfr)
            self.d.find_element_by_id('switcher_plogin').click()
            time.sleep(1)
            self.d.find_element_by_id('u').clear()
            self.d.find_element_by_id('u').send_keys(self.user_info['account'])
            time.sleep(0.5)
            self.d.find_element_by_id('p').send_keys(self.user_info['password'])
            time.sleep(1)
            self.d.find_element_by_id('login_button').click()
            time.sleep(1)

            try:
                # 等待是否出现验证码 并 判断是否登陆成功, 10s超时
                vcodeIfr = WebDriverWait(self.d, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#newVcodeIframe iframe')))
                abs_x = vcodeIfr.location['x'] + abx
                abs_y = vcodeIfr.location['y'] + aby
                btn_height = abs_y + 306
                self.d.switch_to.frame(vcodeIfr)  # 切换到内层iframe
                self.deal_vc(abs_x, abs_y, btn_height)
                # time.sleep(5)   # 临时手动测试
            except Exception:
                logger.info('no verify, pass step')
            logger.info('login success')
            logger.info('%s\t\tpwd:  %s' % (self.user_info['account'], self.user_info['password']))
            # 获取刚刚登录后的cookie, 有skey就是登录成功
            # res = self.is_login()
            res = self.tim_login_process()
            if res['succ']:
                return {'succ': True, 'cookies': res['cookies']}
            else:
                return {'succ': False, 'msg': 'cookie has no skey'}

        except Exception as e:
            logger.error(e, exc_info=1)
            return {'succ': False, 'msg': e}
