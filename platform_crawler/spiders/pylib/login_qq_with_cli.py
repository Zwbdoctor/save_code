import os
import time
import win32gui
import psutil
import logging
from ctypes import windll
from platform_crawler.settings import join, IMG_PATH, GlobalVal, GlobalFunc
from platform_crawler.configs.excute_paths import ExecutePaths


ACC, u, pag, logger = None, None, None, None
TIM_IMG_PATH = join(IMG_PATH, 'tim_img')
NEW_ERROR_PATH = join(TIM_IMG_PATH, 'new_error_img')

if not os.path.exists(TIM_IMG_PATH):
    os.makedirs(TIM_IMG_PATH)
if not os.path.exists(NEW_ERROR_PATH):
    os.makedirs(NEW_ERROR_PATH)

img_path = join(TIM_IMG_PATH, 'qq_cli_vc_cf.png')
err_account_img = join(TIM_IMG_PATH, 'err_account.png')
death_acc_img = join(TIM_IMG_PATH, 'death_acc.png')
find_password_img = join(TIM_IMG_PATH, 'find_password.png')
login_success = join(TIM_IMG_PATH, 'login_succ.png')
after_enter_login_btn = join(NEW_ERROR_PATH, 'after_enter.png')
authentication_img = join(TIM_IMG_PATH, 'need_auth.png')
VERIFY_TIMES = 1


def kill_qq(src=True):
    if src:
        GlobalFunc.save_screen_shot(GlobalVal.err_src_name % time.time()*1000)
    for e in psutil.process_iter():
        a = e.name()
        if 'TIM' in a:
            e.kill()


def btn_location(img_name_path, loop_time=2, dur=0):
    # 获取图片位置
    s = time.time()
    for e in range(loop_time):
        try:
            x, y, w, h = pag.locateOnScreen(img_name_path)
            logger.info('Find once cost time: %s' % int(time.time() - s))
            return x, y
        except TypeError:
            if dur != 0:
                time.sleep(dur)
            continue
    else:
        return False


def handle_login_res(loginid):
    result = btn_location(img_path)       # vc page
    if result:
        logger.info('Verify Code Appeared')
        return deal_vc(loginid)
    elif btn_location(err_account_img):     # account error page
        kill_qq()
        logger.info('Wrong account or password!')
        res = False
    elif btn_location(death_acc_img):
        kill_qq()
        logger.info('Frozen account')
        res = False
    elif btn_location(find_password_img):
        kill_qq()
        logger.info('Wrong password! Find and recheck')
        res = False
    elif btn_location(authentication_img):
        kill_qq()
        logger.info('Need to authentication!')
        res = False
    elif btn_location(login_success):
        logger.info('Tim client login success')
        return True
    else:
        logger.info('Unknown situation with account: %s' % ACC)
        GlobalFunc.save_screen_shot(GlobalVal.err_src_name % time.time()*1000)
        res = False
    if not res:
        pic_name = join(NEW_ERROR_PATH, 'error_%s.png' % (int(time.time())))
        pag.screenshot(pic_name)
        return res


def deal_vc(loginid):
    global VERIFY_TIMES
    # cut and deal vc img
    img1_path = join(TIM_IMG_PATH, 'qq_cli_vc.png')
    pag.screenshot(img1_path, region=(loginid[4][0] + 120, loginid[4][1] + 202, 132, 56))
    with open(img1_path, 'br') as f:
        im = f.read()
    res = u.rc.rk_create(im, '2040')
    windll.user32.SetCursorPos(loginid[4][0] + 100, loginid[4][1] + 110)
    pag.typewrite(res.get('Result').lower())
    pag.hotkey('enter')
    time.sleep(0.8)
    if VERIFY_TIMES != 1:
        u.rc.rk_report_error(res.get('Id'))
    VERIFY_TIMES += 1
    return handle_login_res(loginid)


def QQ(qq, pwd):
    # a = win32gui.FindWindow(None, "QQ")
    # 运行QQ
    os.system('"%s"' % ExecutePaths.TimPath)
    time.sleep(5)
    a = win32gui.FindWindow(None, "TIM")  # 获取窗口的句柄，参数1: 类名，参数2： 标题QQ
    loginid = win32gui.GetWindowPlacement(a)
    windll.user32.SetCursorPos(loginid[4][0] + 300, loginid[4][1] + 273)
    pag.click()
    time.sleep(0.2)
    # 输入账号
    pag.typewrite(qq)
    time.sleep(0.2)
    # tab切换
    pag.hotkey('tab')
    pag.typewrite(pwd)
    # 点击回车键登录
    pag.hotkey('enter')
    time.sleep(3)
    pag.screenshot(after_enter_login_btn)
    # 判断是否出现验证码   (90,135)
    res = handle_login_res(loginid)
    if not res:
        return False
    pag.hotkey('enter')
    time.sleep(4)
    a = win32gui.FindWindow(None, "TIM")  # 获取窗口的句柄，参数1: 类名，参数2： 标题QQ
    loginid = win32gui.GetWindowPlacement(a)
    pag.click(loginid[4][2]-68, loginid[4][1]+29)
    # print(68, 29)
    return True


def login_cli(acc, pwd, util):
    global u, pag, logger, ACC
    u = util
    ACC = acc
    pag = util.pag
    logger = logging.getLogger('%s.login_with_tim' % GlobalVal.CUR_MAIN_LOG_NAME)
    kill_qq(src=False)
    return QQ(acc, pwd)


if __name__ == '__main__':
    from platform_crawler.utils.utils import Util
    login_cli('2823259680', 'Hhmt123456', Util())


