from selenium import webdriver
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from PIL import Image
from PIL import ImageEnhance
# from chardet import detect
from pytesseract import image_to_string
import time
import pyautogui as pag
# import traceback
import random
# import win32clipboard as wc
import os
import logging

# from gj_bank.send_keys_win32.key_code import VK_CODE_WIN
# from gj_bank.send_key_pywinio import key_input
# from gj_bank.vkcode import VK_CODE
from pwd import pkey
from platform_crawler.utils.utils import Util
from apis.rk import RClient


# 初始化对象
logger = logging.getLogger('jiaohang')
util = Util()

# 初始化全局变量
bun = ''
un = ''
pw = ''
driver_imgs_path = os.path.join(os.path.abspath('.'), 'jiaohang_imgs\\')
verify_code_img_path = driver_imgs_path + 'verify.png'
passwd_img_path = driver_imgs_path + 'passwd_img.png'
wrong_verify_code = driver_imgs_path + 'wrong_verify_code.png'
wrong_pwd_img_path = driver_imgs_path + 'wrong_pwd.png'
login_succ = driver_imgs_path + 'login_succ.png'
login_result = driver_imgs_path + 'last.png'

# 打码平台对象
code_pwd = pkey['ruokuai']['pw'].encode('utf-8')
rc = RClient(pkey['ruokuai']['un'], code_pwd, '1', 'b40ffbee5c1cf4e38028c197eb2fc751')


def make_randnum(old_num):
    while True:
        num = random.randrange(1, 4)
        if num != old_num:
            break
    return num


def verify_img(img_path, deal_num=2.5):
    """识别验证码"""
    im = Image.open(img_path)
    im = im.convert('L')
    im = ImageEnhance.Contrast(im)
    # 调节精细程度
    im = im.enhance(deal_num)
    # img_data = image_to_string(im, lang="eng")
    img_data = image_to_string(im)
    
    print('before: ' + img_data)
    img_data = ''.join([e.lower() for e in img_data if e != ' ' and e.isalnum()])
    if len(img_data) != 5:
        # num = make_randnum(deal_num)
        # return verify_img(img_path, deal_num=num)
        return False

    # print("img_path:" + img_path)
    print("img_data:" + img_data)
    return img_data


def deal_verify_code(d, used=True):
    """对识别错误的验证码进行处理"""
    verify_code = verify_img(verify_code_img_path) if not used else False
    # 验证码错误，更新验证码并重新识别
    while not verify_code:
        d.find_element_by_id('checkcode').click()     # 点击更新
        time.sleep(1)
        # screenWidth, screenHeight = pag.size()
        pag.click(871, 590)
        time.sleep(3)
        # 裁剪验证码 
        element = d.find_element_by_id('checkcode')
        util.cutimg_dy_driver(d, element, verify_code_img_path) # 重新裁剪
        verify_code = verify_img(verify_code_img_path)
    return verify_code


def deal_res_err(d):
    """处理点击登录后的结果"""
    # from selenium.webdriver.support import expected_conditions as EC
    if util.btn_location(login_succ):            # login success
        return {'type': 'result', 'status': True}
    # 判断验证码是否正确
    elif util.btn_location(wrong_verify_code):
        # d.back()
        return {'type': 'verify_code', 'status': False}
    # 判断密码是否正确
    elif util.btn_location(wrong_pwd_img_path):
        # 密码错误同上 , 回退重新登录
        d.back()
        return {'type': 'pwd', 'status': False}

def rk_read_verify(img_path):
    # 打码平台
    with open(img_path, 'rb') as img:
        im = img.read()
    verify_code = rc.rk_create(im, 3050)
    # print(verify_code)
    return verify_code


def login(d):
    d.get('https://ebank.95559.com.cn/CEBS/cebs/logon.do?bocom_locale_langFlg=zh_CN')
    time.sleep(3)
    cookies = d.get_cookies()
    d.find_element_by_id('cstNo').send_keys(bun)    # 输入网银客户号
    d.find_element_by_id('oprName').send_keys(un)   # 输入用户名
    util.input_sth(passwd_img_path, pw)             # 输入密码
    time.sleep(0.5)
    # 裁剪验证码
    element = d.find_element_by_id('checkcode')         # 定位验证码
    util.cutimg_dy_driver(d, element, verify_code_img_path)
    # 获取验证码
    # verify_code = deal_verify_code(d, used=False)
    verify_code = rk_read_verify(verify_code_img_path)['Result'].lower()
    # 输入验证码
    # util.input_sth('./driver_imgs/veri_code.png', verify_code)
    d.find_element_by_id('dynamicCode').send_keys(verify_code)
    # 点击登录
    d.find_element_by_id('submitButton1').click()
    time.sleep(3)

    # 判断结果
    res = deal_res_err(d)
    d.save_screenshot(login_result)     # 监控性截图
    if res['type'] == 'result' and res['status'] == True:
        sessionid = d.get_cookie('JSESSIONID')['value']
        cookies = "com.bocom.cebs.base.resolver.CEBSSmartLocaleResolver.LOCALE=zh_CN; JSESSIONID=%s" % sessionid
        return cookies
    elif res['type'] == 'verify_code':
        return login(d)
    else:
        return login(d)


def get_task_parm():
    d = webdriver.Ie()
    d.maximize_window()
    while True:
        try:
            logger.info('do run task')
            cookies = login(d)
            d.quit()
            msg = u'RUNTASK：data---\n%s' % (cookies)
            logger.info(msg)
            return {'type': 3, 'username': bun, 'bcm_cookie': cookies}
        except Exception as e:
            logger.error(e, exc_info=True)
            d.quit()
            time.sleep(3) 
            return get_task_parm()


def do_task_jiaohang(p):
    global bun, un,pw
    bun = p['bun']
    un = p['un']
    pw = p['pwd']
    return get_task_parm()
