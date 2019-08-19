import subprocess
import logging
import time
import os
from logging.handlers import TimedRotatingFileHandler

hd = logging.getLogger('ss')
logging.basicConfig(level=logging.DEBUG)
fh = TimedRotatingFileHandler('ss.log', when='S', interval=3, backupCount=3)
fh.setLevel(logging.DEBUG)
hd.addHandler(fh)


wxp = 'E:\Program Files (x86)\Tencent\WeChat\WeChat.exe'

wx = subprocess.Popen([wxp])
print(wx.poll())
# os.system(wxp)
inmsg = 'info msg'
for e in range(30):
    wx = subprocess.Popen([wxp])
    # wx.kill()
    hd.info(inmsg)
    time.sleep(0.3)
    # if e == 25:
        # del(wx)
        # inmsg = 'after del wx pid info msg'



