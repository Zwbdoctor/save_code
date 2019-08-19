#!/usr/bin/env python
# coding:utf-8

import requests
from time import strftime
from hashlib import md5
import base64
import json


class RClient(object):

    def __init__(self, username, password, soft_id, soft_key):
        self.username = username
        self.password = md5(password).hexdigest()
        self.soft_id = soft_id
        self.soft_key = soft_key
        # self.base_params = {
        #     'username': self.username,
        #     'password': self.password,
        #     'softid': self.soft_id,
        #     'softkey': self.soft_key,
        # }
        self.base_params = {"username": username, "password": self.password,
                            "typeid": "", "timeout": 60, "softid": soft_id,
                            "softkey": soft_key, 'image': ''}
        self.headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-cn',
            'Content-Type': 'application/json',
            'Connection': 'Keep-Alive',
            'Expect': '100-continue',
            'Host': 'api.ruokuai.com',
            'User-Agent': 'ben',
        }

    def rk_create(self, im, im_type, timeout=60):
        """
        im: 图片字节
        im_type: 题目类型
        """
        params = {
            'typeid': im_type,
            'timeout': timeout,
            # 'image': 'data:image/jpg;base64,'+base64.b64encode(im).decode()
            'image': base64.b64encode(im).decode()
        }
        self.base_params.update(params)
        print(self.base_params)
        r = requests.post('http://api.ruokuai.com/create.json', data=json.dumps(self.base_params), headers=self.headers)
        return r.json()

    def rk_report_error(self, im_id):
        """
        im_id:报错题目的ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://api.ruokuai.com/reporterror.json', data=params, headers=self.headers)
        return r.json()

    def rk_report(self, im, im_type, vn, timeout=60):
        very_str = f'verify_str_{strftime("%Y-%m-%d %H:%M")}'
        vs = md5(very_str.encode('utf-8')).hexdigest()
        url = 'http://144.34.194.228/upImg/%s/%s/%s' % (im_type, vn, vs)
        resp = requests.post(url, files={'image': ('%s.png' % vn, im)}, timeout=timeout)
        print(resp.text)


if __name__ == '__main__':
    rc = RClient('sz1992103', 'qaz123wsx456'.encode('utf-8'), 1, 'b40ffbee5c1cf4e38028c197eb2fc751')
    import os
    fn = os.path.join(os.path.abspath('../imgs'), 'vc_img.png')
    im = open(fn, 'rb').read()
    # print(base64.b64encode(im))
    print(rc.rk_create(im, 3040))
#     # print(rc.rk_report_error('8ef97f93-e8e7-4316-96e6-fe206c87b2fc'))

