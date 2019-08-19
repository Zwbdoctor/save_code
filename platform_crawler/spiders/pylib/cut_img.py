from subprocess import Popen
from multiprocessing import Process     # , Manager
import time
import os
import traceback
import logging

from platform_crawler.utils.utils import Util
from platform_crawler.send_keys_win32 import sendkeys
from platform_crawler.settings import join, IMG_PATH, temp_path, GlobalVal
from platform_crawler.configs.excute_paths import ExecutePaths

u = Util()


logger = None
fscapture = ExecutePaths.FsCapturePath
img_temp_path = temp_path


def cut_img(height, dir_path, pic_name, start_point=None, end_point=None, click_point=None):
    global logger
    logger = logging.getLogger('%s.cut_img' % GlobalVal.CUR_MAIN_LOG_NAME)
    start_point = [0, 29] if not start_point else start_point
    click_point = [1058, 535] if not click_point else click_point
    end_point = [1899, 1035] if not end_point else end_point

    p = Process(target=run_cut_img, args=(height, dir_path, pic_name, start_point, click_point, end_point))
    st = time.time()
    p.start()
    p.join(timeout=50)
    if time.time() - st > 50:
        # kill 子进程
        p.terminate()
        reset_mouse_and_kbd()
        res = {'succ': False, 'msg': 'get img time out, pic_name: %s---dir_path: %s' % (pic_name, dir_path)}
    else:
        res = {'succ': True}
    logger.info('time duration: %s' % (int(time.time() - st)))
    return res


def reset_mouse_and_kbd():
    # 恢复鼠标键盘状态
    try:
        u.pag.keyUp('ctrl')
        u.pag.hotkey('esc')
    except:
        pass


def run_cut_img(height, dir_path, pic_name, start_point, click_point, end_point):
    """
    拉动裁剪框，截取图片
    :param height: 页面高度
    :return: bool(True,False)
    """
    clear_imgs()
    if height and height > 900:
        fs = long_pic_cut(height, start_point, click_point, end_point)
    else:
        fs = Popen([fscapture])
        u.pag.hotkey('alt', 'prtscr', interval=0.5)
        time.sleep(1)
    move_img(dir_path, pic_name, fs)


def driver_scroll(height, driver, js):
    for e in range(0, height, 100):
        driver.execute_script(js % e)


def long_pic_cut(height, start_point, click_point, end_point):
    """截取长图片（包含url）"""
    fs = Popen([fscapture])
    u.click_img_center(join(IMG_PATH, 'cut_btn.png'))
    time.sleep(1.5)
    u.pag.moveTo(*start_point)
    u.pag.keyDown('ctrl')
    time.sleep(1)
    u.pag.click(*start_point)
    time.sleep(1)
    u.pag.moveTo(*end_point, duration=0.3)
    u.pag.click(*end_point)
    u.pag.keyUp('ctrl')
    time.sleep(1)
    u.pag.click(*click_point)
    time.sleep(1)
    u.pag.click(900, 60)

    wtimes = int(height/100) + 1
    sendkeys.mouse_wheel_loop(wtimes)
    time.sleep(3)
    u.pag.hotkey('esc', interval=0.2)
    return fs


def move_img(dir_path, picname, fs):
    """
    移动图片
    :param dir_path: 本地图片路径
    :param picname: 图片名称
    :param fs: 截图进程
    :return: 是否成功
    """
    try:
        st = time.time()
        while True:
            f_list = os.listdir(img_temp_path)
            if f_list:
                time.sleep(1)
                fs.kill()
                time.sleep(0.5)
                with open(os.path.join(img_temp_path, f_list[0]), 'br') as old:
                    oi = old.read()
                with open(os.path.join(dir_path, picname), 'bw') as newf:
                    newf.write(oi)
                return {'succ': True}
            elif time.time() - st > 5:      # 超过5秒没得到
                fs.kill()
                print('not get pic after 5 seconds')
                return {'succ': False, 'msg': 'not get pic after 5 seconds'}
    except Exception as e:
        return {'succ': False, 'msg': traceback.format_exc()}


def clear_imgs():
    """清楚可能存在的图片"""
    f_list = os.listdir(img_temp_path)
    if f_list:
        for e in f_list:
            os.remove(os.path.join(img_temp_path, e))
