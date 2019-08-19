from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import pyautogui as pag
import random
import os
import logging

# from pwd import pkey
from platform_crawler.utils.utils import Util
# from apis.rk import RClient
# from apis.rk_v2 import APIClient


# 初始化对象
logger = logging.getLogger('ccbn')
util = Util()

# 初始化全局变量
# driver_imgs_path = os.path.abspath('./spiders')
# passwd_img_path = driver_imgs_path + 'pwd.png'
# wrong_pwd_img_path = driver_imgs_path + 'wrong_pwd.png'
# login_result = driver_imgs_path + 'last.png'
base_path = os.path.abspath('./spiders/ccbn')
verify_code_img_path = os.path.join(base_path, 'verify.png')
passwd_img_path = os.path.join(base_path, 'pwd.png')
wrong_verify_code = os.path.join(base_path, 'vc_error.png')
login_succ = os.path.join(base_path, 'login_success.png')

# 打码平台对象
# code_pwd = pkey['ruokuai']['pw'].encode('utf-8')
# rc = RClient(pkey['ruokuai']['un'], code_pwd, '1', 'b40ffbee5c1cf4e38028c197eb2fc751')


def make_randnum(old_num):
    while True:
        num = random.randrange(1, 4)
        if num != old_num:
            break
    return num


def wait_element(ele_type, ele, wait_time=5):
    el = WebDriverWait(d, wait_time, 0.5).until(EC.visibility_of_element_located((ele_type, ele)))
    return el


def deal_res_err():
    """处理点击登录后的结果"""
    # from selenium.webdriver.support import expected_conditions as EC
    if util.btn_location(login_succ):            # login success
        return {'type': 'login success', 'status': True}
    # 判断验证码是否正确
    elif util.btn_location(wrong_verify_code):
        d.refresh()
        return {'type': 'verify_code', 'status': False}
    else:
        return {'status': False}
    # 判断密码是否正确
    # elif util.btn_location(wrong_pwd_img_path):
        # 密码错误同上 , 回退重新登录
        # d.back()
        # return {'type': 'pwd', 'status': False}


def rk_read_verify(img_path):
    # 打码平台
    with open(img_path, 'rb') as img:
        im = img.read()
    verify_code = util.rc.rk_create(im, 3040)
    # verify_code = input('Please input the verify code\n>>')
    return verify_code


def cutimg_by_driver(d, element, img_path):
    """裁剪验证码---通过无头浏览器"""
    from PIL import Image
    d.save_screenshot(img_path)
    left = element.location['x']
    top = element.location['y']
    elementWidth = left + element.size['width']
    elementHeight = top + element.size['height']
    # left, top, elementWidth, elementHeight = 1014, 354, 1094, 389
    picture = Image.open(img_path)
    picture = picture.crop((left, top, elementWidth, elementHeight))
    picture.save(img_path)
    return True


def login():
    """用户登陆"""
    d.get('https://corp.bank.ecitic.com/cotb/login.html')
    d.implicitly_wait(10)
    time.sleep(5)
    # 输入用户代码
    wait_element(By.NAME, 'userCode').send_keys(un)
    time.sleep(0.5)

    # 输入密码
    util.click_img_center(passwd_img_path)
    pag.typewrite(pw)
    time.sleep(0.5)
    # 裁剪验证码
    # """
    vc_img = d.find_element_by_id('verifyCode')
    cutimg_by_driver(d, vc_img, verify_code_img_path)
    # 获取验证码
    verify_code = rk_read_verify(verify_code_img_path).get('Result').lower()
    # verify_code = rk_read_verify(verify_code_img_path)
    # 输入验证码
    d.find_element_by_id('verifyCodeInput').send_keys(verify_code)
    # d.find_element_by_id('verifyCodeInput').click()
    # pag.typewrite(verify_code)
    # 点击登录
    d.find_element_by_class_name('ec-btn-red').click()
    d.implicitly_wait(10)
    time.sleep(4)
    # """
    # 判断结果
    res = deal_res_err()
    if res.get('type') == 'login success' and res.get('status') == True:
        logger.info('login success!')
        # bsn_code = d.find_element_by_css_selector('#fixedOftenNav ul li:nth-child(1)').get_attribute('data-code')
        bsn_code = '00102011'
        # bsn_code = d.execute_script("return document.querySelector('#fixedOftenNav ul li:nth-child(1)').getAttribute('data-code')")
        # ck = d.execute_script('return document.cookie')
        cookies = d.get_cookies()
        cookies = '; '.join(['%s=%s' % (e.get('name'), e.get('value')) for e in cookies])
        # cookies = '%s; JSESSIONID=%s' % (ck, cookies)
        return bsn_code, cookies
    elif res.get('type') == 'verify_code':
        logger.warning('verify_code error')
        return login()
    else:
        return False


def get_task_parm(param, spider):
    """获取任务参数"""
    global d, un, pw, logger
    logger = logging.getLogger(spider)
    # 判断锁
    try:
        with open('ccbn_lock', 'r') as lk:
            lock = lk.read()
    except:
        lock = ''
    if lock == 'true':
        logger.error('account locked')
        return {'succ': False, 'msg': 'account locked'}

    un, pw = param.get('un'), param.get('pwd')
    d = webdriver.Ie()
    d.maximize_window()
    for e in range(3):
        try:
            cookies = login()
            if not cookies:
                continue
            d.quit()
            return {'succ': True, 'type': 4, 'username': un, 'ccbn_cookie': cookies[1], 'bsn_code': cookies[0]}
        except Exception as e:
            logger.error(e, exc_info=True)
            d.quit()
            return {'succ': False, 'msg': 'unknown error'}
    else:
        with open('ccbn_lock', 'w') as lk:
            lk.write('true')
        return {'succ': False, 'msg': 'login failed after tried 3 times!!!'}


# if __name__ == '__main__':
#     get_task_parm({'un': 'tft125', 'pwd': '58452013'}, 'ccbn')
