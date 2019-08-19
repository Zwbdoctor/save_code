#!/usr/bin/env python
# coding:utf-8

import requests
from hashlib import md5
from time import strftime


class ChaojiyingClient:

    def __init__(self, username, password, soft_id):
        self.username = username
        self.password = md5(password.encode('utf-8')).hexdigest()
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

    def rk_create(self, im, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        # codetype = codetype if codetype == 1902 else 8001
        codetype = 1902
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files,
                          headers=self.headers)
        res = r.json()
        # if '3002' in str(res.get('err_no')):
        if res.get('err_no') == -3002:
            return self.rk_create(im, 1902)
        res['Id'] = res.get('pic_id')
        res['Result'] = res.get('pic_str')
        return res

    def rk_report(self, im, im_type, vn, timeout=60, vc_type='default'):
        very_str = f'verify_str_{strftime("%Y-%m-%d %H:%M")}'
        vs = md5(very_str.encode('utf-8')).hexdigest()
        url = 'http://144.34.194.228:8082/upImg/%s/%s/%s/%s' % (vc_type, im_type, vn, vs)
        try:
            resp = requests.post(url, files={'image': ('%s.png' % vn, im)}, timeout=timeout)
            print(resp.text)
        except:
            print('rk_report connection time out')

    def rk_report_error(self, im_id):
        """
        im_id:报错题目的图片ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
        return r.json()


if __name__ == '__main__':
    chaojiying = ChaojiyingClient('cjyhhmt', 'cjyhhmt1234', '899827')  # 用户中心>>软件ID 生成一个替换 96001
    im = open('./from_page/r7stu.png', 'rb').read()                     # 本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
    print(chaojiying.rk_create(im, 1902))                               # 1902 验证码类型  官方网站>>价格体系 3.4+版 print 后要加()
