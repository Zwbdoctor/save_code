import os
import time
import win32gui
import pyautogui as pag
import psutil
from ctypes import windll


def kill_qq():
    for e in psutil.process_iter():
        a = e.name()
        b = e.as_dict()
        if 'TIM' in a:
            print(a)
            print(b)  
            e.kill()


def QQ(qq, pwd):
    # a = win32gui.FindWindow(None, "QQ")
    # 运行QQ
    os.system('"E:\\Program Files (x86)\\Tencent\\TIM\\Bin\\QQScLauncher.exe"')
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
    time.sleep(4)
    a = win32gui.FindWindow(None, "TIM")  # 获取窗口的句柄，参数1: 类名，参数2： 标题QQ
    loginid = win32gui.GetWindowPlacement(a)
    pag.click(loginid[4][2]-68, loginid[4][1]+29)
    print(68, 29)

    """<span class="err_m" id="err_m">为了更好的保护您的QQ，请使用<a href="http://im.qq.com/mobileqq/2013/" target="_blank">QQ手机版</a>扫描二维码登录。<a href="http://ptlogin2.qq.com/qq_cheat_help" target="_blank">(帮助反馈)</a>(10005)</span>"""
    """
        document.querySelector('#err_m').textContent
        为了更好的保护您的QQ，请使用QQ手机版扫描二维码登录。(帮助反馈)(10005)            判断
        document.querySelector('#qlogin_list .face').click()        # 点击已经登陆的qq登陆
    """

if __name__ == '__main__':
    QQ('1409445787', 'Tempwin2010')
    kill_qq()


