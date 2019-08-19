
def kill_proc():
    from psutil import process_iter
    try:
        for ps in process_iter():
            if 'iexplore' in ps.name() or 'iedriver' in ps.name():
                ps.kill()
    except:
        pass


import psutil
# psutil.Popen(['chrome.exe', '--remote-debugging-port=9222', '--user-data-dir="C:\selenum\AutomationProfile"'])
# chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")


import os, subprocess, time
# os.kill(4368, signal.SIGKILL)


def chr():
    cmd = 'chrome --remote-debugging-port=9222 --user-data-dir=c:\selenium\AutomationProfile'
    os.system(cmd)


if __name__ == '__main__':
    # a = Process(target=chr)
    a = psutil.Popen(['chrome', '--remote-debugging-port=9222', '--user-data-dir=c:\selenium\AutomationProfile'], stdout=subprocess.PIPE)
    a.kill()




