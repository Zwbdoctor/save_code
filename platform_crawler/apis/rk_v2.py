import hashlib
import requests
from datetime import *


class APIClient(object):

    def __init__(self, username, password, soft_id, soft_key):
        self.password = hashlib.md5(password).hexdigest()
        self.paramDict = {
            'username': username, 'password': self.password,
            'timeout': 60, 'softid': soft_id, 'softkey': soft_key
        }
        self.paramKeys = ['username', 'password', 'typeid', 'timeout', 'softid', 'softkey']

    def rk_create(self, im, im_type, timeout=60):
        url = 'http://api.ruokuai.com/create.xml'
        self.paramDict.update({'typeid': int(im_type), 'timeout': timeout})
        result = self.http_upload_image(url, im)
        return result

    def http_upload_image(self, url, filebytes):
        timestr = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        boundary = '------------' + hashlib.md5(timestr.encode()).hexdigest().lower()
        boundarystr = '\r\n--%s\r\n' % (boundary)

        bs = b''
        for key in self.paramKeys:
            bs = bs + boundarystr.encode('ascii')
            param = "Content-Disposition: form-data; name=\"%s\"\r\n\r\n%s" % (key, self.paramDict[key])
            # print param
            bs = bs + param.encode('utf8')
        bs = bs + boundarystr.encode('ascii')

        header = 'Content-Disposition: form-data; name=\"image\"; filename=\"%s\"\r\nContent-Type: image/gif\r\n\r\n' % (
            'sample')
        bs = bs + header.encode('utf8')

        bs = bs + filebytes
        tailer = '\r\n--%s--\r\n' % (boundary)
        bs = bs + tailer.encode('ascii')

        headers = {'Content-Type': 'multipart/form-data; boundary=%s' % boundary,
                   'Connection': 'Keep-Alive',
                   'Expect': '100-continue',
                   }
        response = requests.post(url, params='', data=bs, headers=headers).text
        if '任务超时' in response:
            return {'msg': '任务超时'}
        print(response)
        res = {}
        for i in response.split('\n'):
            if 'Result' in i:
                res['Result'] = i[8:-9]
            elif 'Id' in i:
                res['Id'] = i[4: -5]
        return res

    def rk_report_error(self, *args, **kwargs):
        return

    def rk_report(self, im, im_type, vn, timeout=60):
        # timstr = time.strftime("%Y-%m-%d %H:%M")
        # very_str = f"verify_str_{timstr}"
        # vs = hashlib.md5(very_str.encode('utf-8')).hexdigest()
        # url = 'http://144.34.194.228/upImg/%s/%s/%s' % (im_type, vn, vs)
        # resp = requests.post(url, files={'image': ('%s.png' % vn, im)}, timeout=timeout)
        # print(resp.text)
        return


if __name__ == '__main__':
    rc = APIClient('sz1992103', 'qaz123wsx456'.encode('utf-8'), 1, 'b40ffbee5c1cf4e38028c197eb2fc751')
    import os
    filebytes = open(os.path.join(os.path.abspath('../imgs'), "vc_img.png"), "rb").read()
    print(rc.rk_create(filebytes, 3040))
