import win32gui
import win32con
import re


import time
# import os

titles = []


def EnumWindowsProc (hwnd,mouse):
    # show all the window msg
    if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) != "":
        text = win32gui.GetWindowText(hwnd)
        classname = win32gui.GetClassName(hwnd)
        titles.append({'win_name': text, 'hwnd': hwnd, 'classname': classname})
        # print("the window's text = %s \nhwnd = %d classname = %s" % (text,hwnd,classname))
        # SendMessage(hwnd,win32con.WM_CLOSE,win32con.VK_RETURN,0)
        # win32gui.SetForegroundWindow(hwnd)
        # win32gui.ShowWindow(hwnd,win32con.SW_SHOW)
        # win32gui.ShowWindow(hwnd,win32con.SW_SHOWNORMAL)


def PrintSort_ALL_visable_window():
    win32gui.EnumWindows(EnumWindowsProc, 1)
    lt = [t for t in titles if t]
    for t in lt:
        print(t)


# return an Handle of a window
def GetCurForWin():
    for i in range(1,2):
        time.sleep(1)
        hw = win32gui.GetForegroundWindow()
        text = win32gui.GetWindowText(hw)
        desk = win32gui.GetDesktopWindow()
        print("Current window's hw = %d, desk = %d, text = %s" % (hw,desk,text))


class WindowFinder:
    # "Class to find and make focus on a particular Native OS dialog/Window "
    def __init__ (self):
        self._handle = 527588

    def find_window(self, class_name, window_name = None):
        # "Pass a window class name & window name directly if known to get the window"
        self._handle = win32gui.FindWindow(class_name, window_name)

    def _window_enum_callback(self, hwnd, wildcard):
        if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) != None:
            self._handle = hwnd

    def find_window_wildcard(self, wildcard):
        # "This function takes a string as input and calls EnumWindows to enumerate through all open windows"
        self._handle = None
        win32gui.EnumWindows(self._window_enum_callback, wildcard)

    def set_foreground(self):
        # "Get the focus on the desired open window"
        win32gui.SetForegroundWindow(self._handle)

def SetForWin(hwnd):
    win32gui.SetForegroundWindow(hwnd)
    win32gui.SetWindowPos(hwnd,win32con.HWND_TOP,0,0,0,0,win32con.SWP_SHOWWINDOW)

def GetWindByTitile():
    """显示窗口（此处显示微信）"""
    from win32gui import FindWindow, SetForegroundWindow, ShowWindow, GetWindowText
    from win32con import SW_RESTORE
    hwnd = FindWindow("WeChatMainWndForPC", None)
    # text = GetWindowText(hwnd)
    SetForegroundWindow(hwnd)
    ShowWindow(hwnd,SW_RESTORE)



if __name__ == '__main__':
    PrintSort_ALL_visable_window()
    # print(win32gui.GetDesktopWindow())
    # GetWindByTitile()
