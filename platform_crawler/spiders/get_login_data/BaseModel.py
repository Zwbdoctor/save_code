"""
需手动更改logger名称
"""
import os
import time
import subprocess
import traceback
from psutil import process_iter, Popen
from selenium.webdriver import ChromeOptions
from selenium import webdriver

from platform_crawler.utils.utils import Util
from platform_crawler.settings import join, JS_PATH
from platform_crawler.configs.excute_paths import ExecutePaths

# 初始化全局变量
u = Util()
location_dict = []


class Base:

    def __init__(self, *args, **kwargs):
        self.d = None
        self.debug_chrome = None
        self.debugger_port = 9222
        self.base_profile_name = 'AutomationProfile'
        self.base_chrome_data_dir = ExecutePaths.BaseChromeDataDir

    def init_driver_with_real_chrome(self, profile_name, **kwargs):
        self.open_remote_debug_chrome(profile_name=profile_name, **kwargs)
        co = ChromeOptions()
        co.add_argument('log-level=3')
        co.add_argument('--disable-infobars')
        co.add_argument('--ignore-certificate-errors')
        co.debugger_address = '127.0.0.1:%s' % self.debugger_port
        self.d = webdriver.Chrome(options=co)
        self.d.set_page_load_timeout(60)
        self.d.set_script_timeout(30)
        self.d.delete_all_cookies()
        return self.d

    def build_chrome_params(self, profile_name, debugger_port):
        # dirs
        if profile_name:
            self.base_profile_name = profile_name
        data_dir = join(self.base_chrome_data_dir, self.base_profile_name)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        # debugger port
        if debugger_port != 9222:
            self.debugger_port = debugger_port
        chrome_params = [ExecutePaths.ChromePath, f'--remote-debugging-port={self.debugger_port}',
                         f'--user-data-dir={data_dir}', '--disable-password-generation'
                         '--disable-suggestions-ui']
        return chrome_params

    def open_remote_debug_chrome(self, profile_name=None, debugger_port=9222, use_proxy=False,
                                 proxy_server='127.0.0.1:8889'):
        chrome_params = self.build_chrome_params(profile_name, debugger_port)
        proxy_server = f'--proxy-server={proxy_server}'
        if use_proxy:
            chrome_params.append(proxy_server)
        self.debug_chrome = Popen(chrome_params, stdout=subprocess.PIPE)
        time.sleep(1)
        u.pag.hotkey('winleft', 'up', interval=0.3)

    def close_chrome_debugger(self, delete_user_data=False):
        try:
            self.d.quit()
            # self.debug_chrome.kill()
            os.system(f'taskkill /PID {self.debug_chrome.pid}')
        except:
            pass
        if delete_user_data:
            data_dir = join(self.base_chrome_data_dir, self.base_profile_name)
            os.system(f'rm -rf {data_dir}')

    def open_proc(self):
        subprocess.Popen([ExecutePaths.ChromePath])
        time.sleep(3)
        u.pag.hotkey('winleft', 'up', interval=0.3)

    def kill_chrome(self):
        try:
            for e in process_iter():
                if 'chrome' in e.name() or 'chromedriver' in e.name():
                    os.system(f'taskkill /PID {e.pid}')
                    # e.kill()
        except Exception as e:
            print(e)

    def preload_window(self):
        loadtime = """return {"requestTime":1531198164.528,"startLoadTime":1531198164.528,"commitLoadTime":
        1531198165.871,"finishDocumentLoadTime":1531198168.69,"finishLoadTime":1531198171.872,"firstPaintTime":
        1531198166.734,"firstPaintAfterLoadTime":0,"navigationType":"Other","wasFetchedViaSpdy":false,
        "wasNpnNegotiated":true,"npnNegotiatedProtocol":"http/1.1","wasAlternateProtocolAvailable":false,
        "connectionInfo":"http/1.1"}"""
        repstr = """return {"requestTime":%(requestTime)s,"startLoadTime":%(startLoadTime)s,
        "commitLoadTime":%(commitLoadTime)s,"finishDocumentLoadTime":%(finishDocumentLoadTime)s,
        "finishLoadTime":%(finishLoadTime)s,"firstPaintTime":%(firstPaintTime)s,"firstPaintAfterLoadTime":0,
        "navigationType":"Other","wasFetchedViaSpdy":false,"wasNpnNegotiated":true,"npnNegotiatedProtocol":
        "http/1.1","wasAlternateProtocolAvailable":false,"connectionInfo":"http/1.1"}"""
        cutime = time.time()
        timedict = {'requestTime': int(cutime * 1000) / 1000,
                    'startLoadTime': int(cutime * 1000 + 51) / 1000,
                    'commitLoadTime': int(cutime * 1000 + 102) / 1000,
                    'finishDocumentLoadTime': int(cutime * 1000 + 104) / 1000,
                    'finishLoadTime': int(cutime * 1000 + 105) / 1000,
                    'firstPaintTime': int(cutime * 1000 + 104) / 1000}
        with open(join(JS_PATH, 'preload.js')) as j:
            data = j.read()
        for e in data.split('\n'):
            if e.strip() == loadtime:
                e.replace(loadtime, repstr % timedict)
        self.d.execute_script(data)

    def sys_opera(self, url, delete_cookies, press_sleep=0.0):
        self.kill_chrome()
        try:  # 清空相关cookies
            u.delete_all_cookies(delete_cookies)
            time.sleep(1)
            u.delete_all_cookies(delete_cookies)
        except:
            traceback.print_exc()
            return {'succ': False, 'msg': traceback.format_exc()}
        self.open_proc()
        u.pag.click(140, 115)
        u.pag.hotkey('F6')
        u.pag.typewrite(url, interval=press_sleep)
        time.sleep(0.5)
        u.pag.hotkey('enter')

    def click_function(self):
        """use ot rewrite"""
        pass

    def close_opera(self, opera='close'):
        """opera could be 'close', 'quit"""
        # 登陆操作
        if opera == 'quit':
            u.pag.hotkey('alt', 'F4', interval=0.3)
            time.sleep(1)
        elif opera == 'close':
            u.pag.hotkey('ctrl', 'w', interval=0.3)

    def getCookies(self, host, ck_type='str'):
        # cookies操作
        st = time.time()
        while True:
            try:
                cookie = u.getcookiefromchrome(host=host, ck_type=ck_type)
                if cookie:
                    return {'succ': True, 'msg': cookie}
                print('cookies: %s' % cookie)
                time.sleep(1)
                if time.time() - st > 10:
                    return {'succ': False, 'msg': 'got cookies time out:(10s)'}
            except:
                pass
