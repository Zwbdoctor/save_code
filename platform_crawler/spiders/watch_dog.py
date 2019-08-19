import pyautogui as pag
import os
import time
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QMessageBox, QGridLayout, QLabel, QPushButton, QFrame
from win32gui import FindWindow, SetForegroundWindow, ShowWindow, GetWindowText
from win32con import SW_RESTORE
import win32gui
import win32con

titles = []


def raise_window():
    q = QWidget()
    QMessageBox.about(q,"About","ssefffw3g wefwqe3f")


def EnumWindowsProc (hwnd,mouse):
    # show all the window msg
    if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) != "":
        text = win32gui.GetWindowText(hwnd)
        classname = win32gui.GetClassName(hwnd)
        titles.append({'win_name': text, 'hwnd': hwnd, 'classname': classname})
        # print("the window's text = %s \nhwnd = %d classname = %s" % (text,hwnd,classname))
        # win32gui.SendMessage(hwnd,win32con.WM_CLOSE,win32con.VK_RETURN,0)
        # win32gui.SetForegroundWindow(hwnd)
        # win32gui.ShowWindow(hwnd,win32con.SW_SHOW)
        # win32gui.ShowWindow(hwnd,win32con.SW_SHOWNORMAL)


def PrintSort_ALL_visable_window():
    win32gui.EnumWindows(EnumWindowsProc, 1)
    lt = [t for t in titles if t]
    for t in lt:
        print(t)


def watch(region):
    old = os.path.join(os.path.abspath('.'), 'check_old.png') 
    pag.screenshot(old)               # region=(start_x, start_y, width, height)
    time.sleep(1)
    new = os.path.join(os.path.abspath('.'), 'check_new.png') 
    pag.screenshot(old, region=region)               # region=(start_x, start_y, width, height)
    res = pag.locateOnScreen(old, minSearchTime=2)
    if res is None:
        # TODO: send msg
        # pag.prompt('图案发生变化，请检查！')
        get_wind_by_title('Safari')
    time.sleep(1)


def get_wind_by_title(name):
    """显示窗口"""
    hwnd = FindWindow(None, name)
    # text = GetWindowText(hwnd)
    SetForegroundWindow(hwnd)
    ShowWindow(hwnd,SW_RESTORE)


if __name__ == "__main__":
    # watch((820, 247, 412, 74))
    # raise_window()
    PrintSort_ALL_visable_window()