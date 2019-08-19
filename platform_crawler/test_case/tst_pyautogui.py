import pyautogui as pag
import time

time.sleep(3)
pag.dragTo(1200, 700, duration=3, tween=pag.easeInOutSine)



"""
getPointOnLine
返回已成比例的点的（x，y）元组。沿着两条x，y坐标定义的直线。        coordinate : 坐标

easeInQuad
一个二次tWEEN函数，它开始缓慢，然后加速。     accelerates ： 加速

easeOutQuad
A quadratic tween function that begins fast and then decelerates.       decelerates： 减速

easeInOutQuad
A quadratic tween function that accelerates, reaches the midpoint, and then decelerates.
二次tWEEN函数，加速，到达中点，然后减速。

easeInCubic
A cubic tween function that begins slow and then accelerates.
一个三次tWEEN函数，它开始缓慢，然后加速。

easeOutCubic
A cubic tween function that begins fast and then decelerates.
一个三次tWEN函数，它开始快速然后减速。

easeInOutCubic
A cubic tween function that accelerates, reaches the midpoint, and then decelerates.
一个三次tWEEN函数，加速，到达中点，然后减速。

easeInQuart
A quartic tween function that begins slow and then accelerates.
一个四次tWEN函数，它开始缓慢，然后加速。

easeOutQuart(n)
A quartic tween function that begins fast and then decelerates.
一个四次tWEN函数，它开始快速然后减速。

easeInOutQuart(n)
A quartic tween function that accelerates, reaches the midpoint, and then decelerates.
四次函数，加速，到达中点，然后减速。

easeInQuint
A quintic tween function that begins slow and then accelerates.
一个五次tWEEN函数，它开始缓慢，然后加速。

easeOutQuint
A quintic tween function that begins fast and then decelerates.
一个五次tWEN函数，它开始快速然后减速。

easeInOutQuint(n):
A quintic tween function that accelerates, reaches the midpoint, and then decelerates.
五次tWEEN函数加速，到达中点，然后减速。

easeInSine
A sinusoidal tween function that begins slow and then accelerates.
一个正弦TWEN函数，它开始缓慢，然后加速。

easeOutSine
A sinusoidal tween function that begins fast and then decelerates.
一个正弦TWEN函数，它开始快速然后减速。

easeInOutSine(n)
A sinusoidal tween function that accelerates, reaches the midpoint, and then decelerates.
一个正弦TWEEN函数，加速，到达中点，然后减速。

easeInExpo(n)
An exponential tween function that begins slow and then accelerates.
一个指数tWEN函数，它开始缓慢，然后加速。

easeOutExpo
An exponential tween function that begins fast and then decelerates.
一个指数tWEN函数，它开始快速然后减速。

easeInOutExpo
An exponential tween function that accelerates, reaches the midpoint, and then decelerates.
一个指数tWEEN函数，加速，到达中点，然后减速。

easeInCirc
A circular tween function that begins slow and then accelerates.
一个循环的tWEN函数，它开始缓慢，然后加速。

easeInElastic
An elastic tween function that begins with an increasing wobble and then snaps into the destination.
一种弹性的TWEN函数，从一个增加的摆动开始，然后进入目的地。

easeOutElastic(n, amplitude=1, period=0.3)
An elastic tween function that overshoots the destination and then "rubber bands" into the destination.
一个弹性的TWEN函数，它将目的地超过，然后“橡皮筋”进入目的地。
Args:
  n (float): The time progress, starting at 0.0 and ending at 1.0.

Returns:
  (float) The line progress, starting at 0.0 and ending at 1.0. Suitable for passing to getPointOnLine().

easeInBack
A tween function that backs up first at the start and then goes to the destination.
一个tWEN函数，在开始时先备份，然后转到目的地。

easeOutBack
A tween function that overshoots the destination a little and then backs into the destination.
一个TWEN函数，它稍微超出目的地，然后返回目的地。

easeInOutBack(n, s=1.70158):
A "back-in" tween function that overshoots both the start and destination
一个“向后”的tWEN函数，它超越起点和目的地。

easeInBounce
A bouncing tween function that begins bouncing and then jumps to the destination.
一个跳跃的tWEN函数，它开始弹跳然后跳到目的地。

easeOutBounce
A bouncing tween function that hits the destination and then bounces to rest.
一个跳跃的TWEN函数，击中目标然后反弹休息。
"""