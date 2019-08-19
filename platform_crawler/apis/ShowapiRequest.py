import requests
from base64 import b64encode
from hashlib import md5
from time import strftime

files = {}


class ShowapiRequest:
    def __init__(self, my_appId, my_appSecret):
        self.url = 'http://route.showapi.com/184-5'
        self.body = {
            "showapi_appid": my_appId,
            'showapi_sign': my_appSecret
        }
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/45.0.2427.7 Safari/537.36"}
        self.timeout = None

    def addFilePara(self, key, value_url):
        files[key] = open(r"%s" % (value_url), 'rb')
        return self

    def addHeadPara(self, key, value):
        self.headers[key] = value
        return self

    # 设置连接时间和读取时间
    def setTimeout(self, connecttimout, readtimeout):
        timeouts = {}
        timeouts.update({'connecttimeout': connecttimout, 'readtimeout': readtimeout})
        return timeouts

    def post(self, body):
        timeout = (30, 30) if not self.timeout else None
        # timeout = (timeouts["connecttimout"], timeouts["readtimeout"])
        res = requests.post(self.url, files=files, data=body, headers=self.headers, timeout=timeout)
        return res.json()

    def rk_create(self, im, codetype, to_jpg='1', timeout=60):
        im = b64encode(im).decode()
        codetype = str(codetype).replace('0', '')
        body = {
            'img_base64': im, 'typeId': codetype, 'convert_to_jpg': to_jpg, 'needMorePrecise': '0'
        }
        body.update(self.body)
        if timeout != 60:
            self.timeout = timeout
        res = self.post(body)
        return res.get('showapi_res_body')

    def rk_report_error(self, im_id):
        ...

    def rk_report(self, im, im_type, vn, timeout=60, vc_type='default'):
        very_str = f'verify_str_{strftime("%Y-%m-%d %H:%M")}'
        vs = md5(very_str.encode('utf-8')).hexdigest()
        url = 'http://144.34.194.228:8082/upImg/%s/%s/%s/%s' % (vc_type, im_type, vn, vs)
        try:
            resp = requests.post(url, files={'image': ('%s.png' % vn, im)}, timeout=timeout)
            print(resp.text)
        except:
            print('rk_report connection time out')


if __name__ == '__main__':
    from pwd import pkey
    sec = pkey.get('wwyy')
    s = ShowapiRequest(sec.get('un'), sec.get('pw'))
    # print(s.rk_create(open('./from_page/7pcgb.png', 'br').read(), 35))
    print(s.rk_report(open('./from_page/8hqh3.png', 'br').read(), 3050, '8hqh3', vc_type='XIAOMISTORE'))
