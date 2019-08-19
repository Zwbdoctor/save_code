from selenium import webdriver
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from PIL import ImageGrab
from PIL import Image
from PIL import ImageEnhance
# from chardet import detect
from pytesseract import image_to_string
import time
import pyautogui as pag
# import traceback
import random
import win32clipboard as wc
import win32con
import re
import os
import logging

# from gj_bank.send_keys_win32.key_code import VK_CODE_WIN
from platform_crawler.send_keys_win32.send_key_pywinio import key_input
# from gj_bank.vkcode import VK_CODE
from pwd import pkey
from apis.rk import RClient
from platform_crawler.send_keys_win32.sendkeys_half import KeyPressLower, KeyPressMore

logger = logging.getLogger('gongshang')

# screenWidth, screenHeight = pag.size()
# print '%s: %s' % (screenWidth, screenHeight)
driver_imgs_path = os.path.join(os.path.abspath('.'), 'gonghang_imgs\\')
un = ''
pw = ''
verify_code_img_path = driver_imgs_path + 'verify.png'
passwd_img_path = driver_imgs_path + 'passwd.png'
wrong_verify_code = driver_imgs_path + 'wrong_verify_code.png'
wrong_pwd_img_path = driver_imgs_path + 'wrong_pwd.png'
login_succ = driver_imgs_path + 'login_succ.png'
cross_frame = driver_imgs_path + 'cross_frame.png'
close_sessionid_img_path = driver_imgs_path + 'close_sessionid_img.png'
# cookies_path = 'C:\\Users\\Administrator\\AppData\\Local\\Microsoft\\Windows\\Temporary Internet Files\\Content.IE5\\'
close_cookie_img_path = driver_imgs_path + 'close_cookie_page.png'
cookie_icon_page_path = driver_imgs_path + 'get_cookie_page.png'
input_verify_code_img = driver_imgs_path + 'veri_code.png'
result_img = driver_imgs_path + 'last.png'
# 打码平台对象
code_pwd = pkey['ruokuai']['pw'].encode('utf-8')
rc = RClient(pkey['ruokuai']['un'], code_pwd, '1', 'b40ffbee5c1cf4e38028c197eb2fc751')


def btn_location(img_name_path):
    # 获取图片位置
    # pag.screenshot().save(screen_img_path)   # 实时监控
    try:
        x, y, w, h = pag.locateOnScreen(img_name_path)
    except TypeError:
        return False
    x, y = pag.center((x, y, w, h))  # 获得中心点
    return x, y


def click_events(img_name_path):
    # 点击事件
    data = btn_location(img_name_path)
    if not data:
        data = btn_location(img_name_path)
    pag.click(data[0], data[1])


def input_sth(img_path, data):
    # send_keys to the input box
    click_events(img_path)
    key_input(st=data)


def make_randnum(old_num):
    while True:
        num = random.randrange(1, 4)
        if num != old_num:
            break
    return num


def verify_img(img_path, deal_num=2):
    """识别验证码"""
    im = Image.open(img_path)
    im = im.convert('L')
    im = ImageEnhance.Contrast(im)
    # 调节精细程度
    im = im.enhance(deal_num)
    img_data = image_to_string(im, lang="eng")
    # img_data = image_to_string(im)
    img_data = ''.join([e.lower() for e in img_data if e != ' ' and e.isalnum()])
    if len(img_data) != 4:
        # num = make_randnum(deal_num)
        # return verify_img(img_path, deal_num=num)
        return False

    # print("img_path:" + img_path)
    print("img_data:" + img_data)
    return img_data


def cut_img_failed(d, safe_edit):
    """裁剪验证码"""
    d.save_screenshot(verify_code_img_path)
    element = safe_edit
    left = element.location['x']
    top = element.location['y']
    elementWidth = left + element.size['width']
    elementHeight = top + element.size['height']

    picture = Image.open(verify_code_img_path)
    picture = picture.crop((left, top, elementWidth, elementHeight))
    picture.save(verify_code_img_path)
    print('verify save ok!')
    return True


def cut_img():
    try:
        # 返回图片在屏幕中的位置
        x, y, w, h = pag.locateOnScreen('./imgs/veri_code.png')
        print('x=%s  y=%s  w=%s  h=%s ' % (x, y, w, h))

        x = x + 152
        y = y + 13
        n = x + 80
        m = y + h - 16
        box = (x, y, n, m)
        img = ImageGrab.grab(box)
        img.save(verify_code_img_path)
        return True
    except Exception as e:
        # traceback.print_exc()
        logger.error(e, exc_info=True)
        return False


def deal_verify_code(d):
    """对识别错误的验证码进行处理"""
    cut_img()                                           # 裁剪验证码
    verify_code = verify_img(verify_code_img_path)      # 获取验证码
    print(verify_code)
    # 验证码错误，更新验证码并重新识别
    while not verify_code:
        d.find_element_by_tag_name('img').click()
        time.sleep(1)
        # cut_img_failed(d, safe_edit)
        cut_img()
        verify_code = verify_img(verify_code_img_path)
        print(verify_code)
        time.sleep(1)
    return verify_code


def deal_res_err(d):
    """处理点击登录后的结果"""
    # from selenium.webdriver.support import expected_conditions as EC
    if btn_location(login_succ):            # login success
        return True
        # 验证码格式不正确
    # 判断验证码是否正确
    elif btn_location(wrong_verify_code):
        # 回退重新登录
        d.back()
        return False
    # 判断密码是否正确
    elif btn_location(wrong_pwd_img_path):
        # 密码错误同上
        d.back()
        return False
    try:
        alert = d.switch_to_alert()
        alert.accept()
    except Exception as e:
        # traceback.print_exc()
        logger.error(e, exc_info=True)
    finally:
        return False

def rk_read_verify(img_path):
    # 打码平台
    with open(img_path, 'rb') as img:
        im = img.read()
    verify_code = rc.rk_create(im, 3040)
    # print(verify_code)
    return verify_code


def login(d):
    d.get('https://corporbank-simp.icbc.com.cn/icbc/normalbank/index.jsp')
    time.sleep(3)
    # 跳转首页frame
    d.switch_to.frame('indexFrame')
    # 跳转登录frame
    d.switch_to.frame('pwd_login_iframe')
    d.find_element_by_id('logonCardNum').send_keys(un)  # 输入用户名
    # 输入密码
    input_sth(passwd_img_path, pw)
    time.sleep(0.5)
    # 跳转验证码frame
    d.switch_to.frame('VerifyimageFrame')

    # safe_edit = d.find_element_by_xpath('//*[@id="safeEdit1"]')
    # safe_edit = d.find_element_by_tag_name('img')    # 定位验证码
    # 获取验证码
    cut_img()
    verify_code = rk_read_verify(verify_code_img_path)['Result'].lower()
    print(verify_code)
    # 输入验证码
    input_sth(input_verify_code_img, verify_code)
    time.sleep(3)
    # 跳转到登录frame, 并点击登录
    d.switch_to.default_content()
    d.switch_to.frame('indexFrame')
    d.switch_to.frame('pwd_login_iframe')
    d.find_element_by_id('submitkey').click()
    time.sleep(3)

    # 判断结果
    res = deal_res_err(d)
    d.save_screenshot(result_img)     # 监控性截图
    if not res:
        login(d)
    # d.switch_to.window(d.window_handles[-1])
    return d


def get_sessionid():
    """获取sessionid"""
    screenWidth, screenHeight = pag.size()
    pag.rightClick(screenWidth/2, screenHeight/2)
    key_input(st='v')
    time.sleep(0.5)
    pag.rightClick(screenWidth/2, screenHeight/2)
    key_input(st='s')
    time.sleep(0.5)
    pag.rightClick(screenWidth/2, screenHeight/2)
    key_input(st='o')
    time.sleep(0.5)
    # click_events(close_sessionid_img_path)
    KeyPressMore(('alt', 'F4'))

    # 从剪贴板获取复制到的内容
    wc.OpenClipboard()
    copy_text = wc.GetClipboardData(win32con.CF_TEXT)
    wc.CloseClipboard()
    # code_type = detect(copy_text)['encoding']
    copy_text = copy_text.decode('gb2312', 'ignore')
    sessionid = re.findall(r'dse_sessionId=(\w+)"', copy_text)[0]

    print(sessionid)
    return sessionid

# ########################################################## not debug ##################
def get_cookies_content(cookies_path):
    # files = os.listdir(cookies_path)
    with open(cookies_path, 'br') as f:
        data = f.read()
    # print(detect(data))
    pattern = re.compile(r'<name>(.*?)</name><value>(.*?)</value>')
    clist = pattern.findall(data.decode('utf-8'))
    cookies_keys = ['ar_stat_uv', 'ar_stat_ss', 'SRV_EBANKC_PUJI']
    cookies = '; '.join(['%s=%s' % (e[0], e[1]) for e in clist if e[0] in cookies_keys])
    print(cookies)
    return cookies

def get_cookies():
    screenWidth, screenHeight = pag.size()
    pag.click(screenWidth/2, screenHeight/2)
    # 获取cookies地址（打开查看cookie）页面    
    time.sleep(4)
    # click_location = (866,827)
    # pag.click(click_location[0], click_location[1])
    KeyPressLower('F12')
    time.sleep(3)
    KeyPressLower('alt')
    time.sleep(1)
    KeyPressLower('c')
    time.sleep(1)
    KeyPressLower('i')
    time.sleep(3)
    click_events(cookie_icon_page_path)
    time.sleep(1)
    KeyPressMore(('ctrl', 'c'))   
    wc.OpenClipboard()
    cookies_path = wc.GetClipboardData()
    wc.CloseClipboard()
    KeyPressMore(('ctrl', 'w'))         # 关闭cookie标签页
    # 关闭debug模式
    pag.click(screenWidth/2, screenHeight/2)
    KeyPressLower('F12')
    # 读取cookie文件并获取内容
    cookies = get_cookies_content(cookies_path)
    return cookies

def get_task_parm():
    d = webdriver.Ie()
    d.maximize_window()
    # from selenium.common.exceptions import NoAlertPresentException
    while True:
        try:
            logger.info('do run task')
            login(d)
            sessionid = get_sessionid()
            cookies = get_cookies()
            d.quit()
            msg = u'RUNTASK：data---\n%s\n%s' % (cookies, sessionid)
            logger.info(msg)
            return {'type': 2, 'username':un , 'icbc_sessionId': sessionid, 'icbc_cookie': cookies}
        except Exception as e:
            logger.error(e, exc_info=True)
            d.quit()
            time.sleep(3) 
            return get_task_parm()

def do_task_gongshang(p):
    global un,pw
    un = p['un']
    pw = p['pwd']
    return get_task_parm()

# if __name__ == '__main__':
    # run()
