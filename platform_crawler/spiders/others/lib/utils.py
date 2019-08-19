import os
import logging
import requests
import time

from time import sleep
from hashlib import md5
from PIL import ImageGrab
from PIL import Image
from logging.handlers import TimedRotatingFileHandler   # , SMTPHandler
import pyautogui as pag


class RClient(object):

    def __init__(self, username, password, soft_id, soft_key):
        self.username = username
        self.password = md5(password).hexdigest()
        self.soft_id = soft_id
        self.soft_key = soft_key
        self.base_params = {
            'username': self.username,
            'password': self.password,
            'softid': self.soft_id,
            'softkey': self.soft_key,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'Expect': '100-continue',
            'User-Agent': 'ben',
        }

    def rk_create(self, im, im_type, timeout=60):
        """
        im: 图片字节
        im_type: 题目类型
        """
        params = {
            'typeid': im_type,
            'timeout': timeout,
        }
        params.update(self.base_params)
        files = {'image': ('a.jpg', im)}
        r = requests.post('http://api.ruokuai.com/create.json', data=params, files=files, headers=self.headers)
        return r.json()

    def rk_report_error(self, im_id):
        """
        im_id:报错题目的ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://api.ruokuai.com/reporterror.json', data=params, headers=self.headers)
        return r.json()


class Util:
    pag = pag
    cookiepath = os.environ['LOCALAPPDATA'] + r"\Google\Chrome\User Data\Default\Cookies"
    code_p = 'qaz123wsx456'.encode('utf-8')
    rc = RClient('sz1992103', code_p, '1', 'b40ffbee5c1cf4e38028c197eb2fc751')

    def wait_element(self, driver, wait_sth, wt):
        from selenium.webdriver.support.wait import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        try:
            ele = WebDriverWait(driver, wt).until(
                EC.presence_of_element_located(wait_sth))
            return ele
        except Exception as er:
            return False

    def btn_location(self, img_name_path, loop_time=10):
        # 获取图片位置
        # from time import time
        # s = time()
        for e in range(loop_time):
            try:
                x, y, w, h = pag.locateOnScreen(img_name_path)
                x, y = pag.center((x, y, w, h))  # 获得中心点
                # print(int(time() - s))
                return x, y
            except TypeError:
                continue
        else:
            return False

    def click_point(self, x, y, left=True):
        if not left:
            pag.rightClick(x, y)
        pag.click(x, y)

    def click_img_center(self, img_name_path):
        # 点击事件
        data = self.btn_location(img_name_path)
        if not data:
            return False
        pag.click(data[0], data[1])
        sleep(0.5)
        return True

    def cutimg_by_driver(self, d, element, img_path, abx=None, aby=None, chx=None, chy=None):
        """裁剪验证码---通过无头浏览器"""
        d.save_screenshot(img_path)
        left = element.location['x']
        top = element.location['y']
        if abx:
            left = element.location['x'] + abx
            top = element.location['y'] + aby
        elementWidth = left + element.size['width']
        elementHeight = top + element.size['height']
        if chx:
            elementWidth += chx
            elementHeight += chy
        picture = Image.open(img_path)
        picture = picture.crop((left, top, elementWidth, elementHeight))
        picture.save(img_path)
        # print('verify save ok: %s' % img_path)
        return True

    def cut_img(self, img_path, box_location):
        """
        裁剪图片--by pyautogui
        box_location = (x, y, m, n) (m,n 为对角坐标)
        """
        try:
            img = ImageGrab.grab(box_location)
            img.save(img_path)
            return True
        except:
            return False

    def record_log(self, log_path, logger_name):
        filename = os.path.join(log_path, '%s.log' % logger_name)
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        formater = logging.Formatter("%(levelname)s - %(asctime)s - %(filename)s[line:%(lineno)d]: %(message)s")
        tf_handler = TimedRotatingFileHandler(filename=filename, when='D', interval=1, backupCount=1, encoding='utf-8')
        tf_handler.setLevel(logging.DEBUG)
        tf_handler.setFormatter(formater)

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(formater)

        # logger.addHandler(tf_handler)
        logger.addHandler(console)
        return logger

    def mDays(self, year, month):
        d30 = [4, 6, 9, 11]
        d31 = [1, 3, 5, 7, 8, 10, 12]
        m2 = 29 if year/4 == 0 and year/4 != 0 else 28
        if month in d30:
            days = 30
        elif month in d31:
            days = 31
        else:
            days = m2
        return days

    def get_date(self, year, m):
        z = lambda x:  x if len(str(x)) == 2 else '0%s' % x
        end = self.mDays(year, m)
        start = '%s-%s-01' % (year, z(m))
        end = '%s-%s-%s' % (year, z(m), end)
        return start, end

    def make_months(self, ms=None, ys=None, mee=None, ye=None):
        mths = []
        year, month, cDay = time.strftime('%Y-%m-%d').split('-')
        ms = int(month)-1 if not ms else ms  # 开始月份 defaul: 前一个月
        ys = int(year) if not ys else ys
        ye = int(year) if not ye else ye
        mee = int(month) if not mee else mee
        med = 13      # month end default
        for y in range(ys, ye+1):
            if y == ye:  # 控制结束月份
                med = mee + 1
            for m in range(ms, med):
                mths.append((y, m))
            ms = 1
        return mths

    def make_dates(self, ms=None, ys=None, me=None, ye=None):
        """
        生成一段时间中，每个月的开始和结束日期
        :param ms: start month
        :param ys: start year
        :param mee: end month
        :param ye: end year
        :return: two list [(year,month), ()], [(startdate, enddate),()]
        """
        mths = self.make_months(ms=ms, ys=ys, mee=me, ye=ye)
        year, month, cDay = time.strftime('%Y-%m-%d').split('-')
        z = lambda x: x if len(str(x)) == 2 else '0%s' % x
        dates = []
        for y, m in mths:
            if y == int(year) and m == int(month):
                day = cDay if cDay == '01' else int(cDay)-1
                dates.append(('%s-%s-01' % (y, z(m)), '%s-%s-%s' % (y, z(m), z(day))))
            else:
                dates.append(self.get_date(y, m))
        return mths, dates

    def make_days(self, ms=None, ys=None, me=None, ye=None):
        """生成天：eg: [day1, day2, day3...]"""
        mths = self.make_months(ms=ms, ys=ys, mee=me, ye=ye)
        year, month, cDay = time.strftime('%Y-%m-%d').split('-')
        z = lambda x: x if len(str(x)) == 2 else '0%s' % x
        days = []               # --------------------old version (days)
        for y, m in mths:
            dl = self.mDays(int(y), int(m))
            if y == int(year) and m == int(month):
                days.extend(['%s-%s-%s' % (y, z(m), z(x)) for x in range(1, int(cDay))])
            else:
                days.extend(['%s-%s-%s' % (y, z(m), z(x)) for x in range(1, dl + 1)])
        return mths, days


