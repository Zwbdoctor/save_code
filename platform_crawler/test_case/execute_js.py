from selenium import webdriver
import time

d = webdriver.Chrome()
d.delete_all_cookies()
url = 'http://www.etjg.com/member/'
d.get(url)
ck = 'xsp__memauth=c67ee84f0efc04d4JOYDuNZ8avvHQqA9IBOKivpggR0cEv03QFirEm5FXEa6292nAbQ2Rq9V3bj%2Bv56NVY%2FQjKjAmWnTbsUyIlMKgUwL9bdt%2FSzy6ycMlnWO53DikEfAB9AbrikJGSoxzwCic%2FEg8p4x; xsp__memauthMd5s=4f0654264dffb3be11ec0debe2b; PHPSESSID=2met8h36eegon15knivjuk1oo-1'
cks = [{'name': e.split('=')[0], 'value': e.split('=')[1]} for e in ck.split('; ')]
for c in cks:
    d.add_cookie(c)


d.get(url)
d.quit()
