# from send_keys_win32 import sendkeys
import time
import pickle
import pyautogui as pag

a1, a2, a3 = 1, 2, 3
# x: x_current, xr: x_relative, xl: x_last


def run():
    # st = time.time()
    while True:
        xl, yl = pag.position()
        if xl >= 1081 and xl <= 1319 and yl >= 484 and yl <= 516:
            break
        print(xl, yl)
        time.sleep(0.1)

    mouse_pos = []
    xf = xl         # 起始点
    print('start to print pos')
    while True:
        x, y = pag.position()
        xr = x - xl
        yr = y - yl
        print(xr, yr)
        mouse_pos.append([xr, yr])
        xl, yl = x, y
        time.sleep(0.01)
        if x > 1319:
            break

    print(mouse_pos)
    stm = 0.01
    mp = []
    for e in mouse_pos:
        if e == [0, 0]:
            stm += 0.01
            continue
        else:
            stm = int(stm*100)/100
        mp.append([e[0], e[1], stm])
        stm = 0.01

    print('==============================================')
    print(mp)

    # with open('line5.dat', 'bw') as f:
    #     pickle.dump(mp, f)


def read_line():
    with open('../utils/line5.dat', 'br') as f:
        data = pickle.load(f)
    print(data)
    # data.remove(data[1])
    # with open('../utils/line5.dat', 'bw') as f:
    #     pickle.dump(data, f)


if __name__ == '__main__':
    run()
    # read_line()
