import cv2
import numpy as np
from os.path import join, exists
from os import makedirs

from platform_crawler.settings import join, IMG_PATH


absp = join(IMG_PATH, 'slip_vc_imgs')
if not exists(absp):
    makedirs(absp)


def show(name):
    cv2.imshow('Show', name)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def vc_location(box, bg):
    # otemp = join(absp, box)
    # oblk = join(absp, bg)
    target = cv2.imread(box, 0)
    template = cv2.imread(bg, 0)
    # w, h = target.shape[::-1]
    temp = join(absp, 'temp.jpg')
    targ = join(absp, 'targ.jpg')
    cv2.imwrite(temp, template)
    cv2.imwrite(targ, target)
    target = cv2.imread(targ)
    target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
    target = abs(255 - target)
    cv2.imwrite(targ, target)
    target = cv2.imread(targ)
    template = cv2.imread(temp)
    result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
    x, y = np.unravel_index(result.argmax(), result.shape)
    # 展示圈出来的区域
    # cv2.rectangle(template, (y, x), (y + w, x + h), (7, 249, 151), 2)
    # show(template)
    y = y * (280/680) + 13 + 17         # + 外边框 + 二分距离
    print(y, x)
    return int(y), x


if __name__ == '__main__':
    bg = join(absp, 'bg.jpg')
    box = join(absp, 'box.png')
    vc_location(box, bg)
