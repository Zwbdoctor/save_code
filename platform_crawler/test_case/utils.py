import random
import os
import logging
import sqlite3
import time

from time import sleep
from PIL import ImageGrab
from PIL import Image
from logging.handlers import TimedRotatingFileHandler, SMTPHandler
import pyautogui as pag
import win32clipboard as wc
# import win32con

# from send_keys_win32.send_key_pywinio import key_input
from win32.win32crypt import CryptUnprotectData
from pwd import pkey
from apis.rk import RClient


class Util:
    pag = pag
    cookiepath = os.environ['LOCALAPPDATA'] + r"\Google\Chrome\User Data\Default\Cookies"
    # 打码平台对象
    code_pwd = pkey['ruokuai']['pw'].encode('utf-8')
    rc = RClient(pkey['ruokuai']['un'], code_pwd, '1', 'b40ffbee5c1cf4e38028c197eb2fc751')

    def get_cks(self, sql):
        cks = []
        with sqlite3.connect(self.cookiepath) as conn:
            cu = conn.cursor()
            cookies = cu.execute(sql).fetchall()
            for host_key, name, encrypted_value,path,expires in cookies:
                ck = {}
                ck['domain'] = host_key
                ck['name'] = name
                ck['path'] = path
                try:
                    ck['value'] = CryptUnprotectData(encrypted_value)[1].decode()
                except:
                    ck['value'] = encrypted_value
                cks.append(ck)
        return cks

    def wait_element(self, driver, wait_sth, wt):
        from selenium.webdriver.support.wait import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        try:
            ele = WebDriverWait(driver, wt).until(
                EC.presence_of_element_located(wait_sth))
            return ele
        except Exception as er:
            return False

    def delete_cookie(self, host):
        sql = "delete from cookies where host_key='%s'" % host
        with sqlite3.connect(self.cookiepath) as conn:
            cu = conn.cursor()
            cu.execute(sql)
            conn.commit()

    def delete_all_cookies(self, hosts):
        if isinstance(hosts, list):
            for h in hosts:
                self.delete_cookie(h)
        else:
            self.delete_cookie(hosts)

    def getcookiefromchrome(self, host=None, ck_type='str'):
        sql = "select host_key,name,encrypted_value,path,expires_utc from cookies where host_key='%s'"
        # sql="select host_key,name,encrypted_value from cookies;"
        # sql = "select * from cookies where host_key='%s';"
        cks = []
        if isinstance(host, list):
            for h in host:
                cks.extend(self.get_cks(sql % h))
            return cks
        else:
            cks.extend(self.get_cks(sql % host))
        if ck_type == 'json':
            return cks
        else:
            ck = '; '.join(['%s=%s' % (e['name'], e['value']) for e in cks])
            return ck

    def btn_location(self, img_name_path, loop_time=10):
        # 获取图片位置
        # pag.screenshot().save(screen_img_path)   # 实时监控
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

    # def winio_input_sth(self, img_path, data):
        # send_keys to the input box
        # self.click_img_center(img_path)
        # key_input(st=data)

    def make_randnum(self, old_num):
        while True:
            num = random.randrange(1, 4)
            if num != old_num:
                break
        return num

    def get_clipboard_data(self):
        try:
            wc.OpenClipboard()
            data = wc.GetClipboardData()
        finally:
            wc.CloseClipboard()
        return data

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

    def record_log_v1(self, filename, logger_name):
        logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
        logger = logging.getLogger(logger_name)
        formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
        # 日志文件handler
        fh = TimedRotatingFileHandler(filename=filename, when="midnight", interval=1, backupCount=3)
        fh.setLevel(logging.INFO)  # 输出到file的log等级的开关
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        # 添加控制台handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger

    def record_log(self, log_path, logger_name):
        filename = os.path.join(log_path, '%s.log' % logger_name)
        err_file_name = os.path.join(log_path, '%s_error.log' % logger_name)
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        formater = logging.Formatter("%(levelname)s - %(asctime)s - %(filename)s[line:%(lineno)d]: %(message)s")
        # formater = logging.Formatter("%(levelname)s - %(asctime)s - %(name)s[line:%(lineno)d]: %(message)s")
        tf_handler = TimedRotatingFileHandler(filename=filename, when='midnight', interval=1, backupCount=7, encoding='utf-8')
        tf_handler.setLevel(logging.DEBUG)
        tf_handler.setFormatter(formater)

        ef_handler = TimedRotatingFileHandler(filename=err_file_name, when='midnight', interval=1, backupCount=7, encoding='utf-8')
        ef_handler.setLevel(logging.ERROR)
        ef_handler.setFormatter(formater)

        smtp_handle = SMTPHandler('smtp.163.com', 'zwbworkmail@163.com', '15638280592@163.com', 'taskSpider',
                                   credentials=('zwbworkmail', 'q512468932'))
        smtp_handle.setLevel(logging.CRITICAL)
        smtp_handle.setFormatter(formater)

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(formater)

        logger.addHandler(tf_handler)
        logger.addHandler(ef_handler)
        logger.addHandler(smtp_handle)
        logger.addHandler(console)
        return logger

    def get_wind_by_title(self):
        """显示窗口（此处显示微信）"""
        from win32gui import FindWindow, SetForegroundWindow, ShowWindow, GetWindowText
        from win32con import SW_RESTORE
        hwnd = FindWindow("WeChatMainWndForPC", None)
        # text = GetWindowText(hwnd)
        SetForegroundWindow(hwnd)
        ShowWindow(hwnd,SW_RESTORE)

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
        if ms == 0:
            ms, ys = 12, int(year)-1
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



