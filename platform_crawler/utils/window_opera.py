import win32gui
import win32con
import subprocess
import time
import os
from send_mail import run_send

tm_hand = None


def find_all_window_class(hwnd, mouse):
    global tm_hand
    if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) != "":
        text = win32gui.GetWindowText(hwnd)
        # classname = win32gui.GetClassName(hwnd)
        # print("the window's text = %s \nhwnd = %d classname = %s" % (text,hwnd,classname))
        # if text == '微信' and classname == 'WeChatMainWndForPC':
        if text == 'TeamViewer':
            win32gui.SetForegroundWindow(hwnd)
            win32gui.ShowWindow(hwnd,win32con.SW_SHOWNORMAL)
            tm_hand = hwnd

def sh_win():
    win32gui.EnumWindows(find_all_window_class, 1)

def open_teamviewer():
    tmv = 'C:\Program Files (x86)\TeamViewer\TeamViewer.exe'
    p = subprocess.Popen([tmv])

def send_pic():
    img_path = 'G:\python_work\python\commen\img_temp'
    imgs = os.listdir(img_path)
    if len(imgs) > 0:
        for i in imgs:
            os.remove(os.path.join(img_path, i))
    fs = r'D:\fscapture\FSCapture.exe'
    f = subprocess.Popen([fs])
    import pyautogui as pag
    pag.hotkey('alt', 'prtscr', interval=0.4)
    for e in range(1000):
        imgs = os.listdir(img_path)
        if len(imgs) > 0:
            break
        time.sleep(0.5)
    win32gui.CloseWindow(tm_hand)
    img_name = os.path.join(img_path, imgs[0])
    run_send(img_name)
    f.kill()

def run():
    open_teamviewer()
    time.sleep(5)
    sh_win()
    send_pic()


if __name__ == '__main__':
    run()
