import requests
import hashlib
import time
import json

FATEA_PRED_URL = "http://pred.fateadm.com"


class TmpObj:
    def __init__(self):
        self.value = None


def CalcSign(pd_id, passwd, timestamp):
    # 加密
    md5 = hashlib.md5()
    md5.update((timestamp + passwd).encode())
    csign = md5.hexdigest()

    md5 = hashlib.md5()
    md5.update((pd_id + timestamp + csign).encode())
    csign = md5.hexdigest()
    return csign


def HttpRequest(url, body_data, img_data="", timeout=20):
    # rsp = Rsp()
    post_data = body_data
    files = {
        'img_data': ('img_data', img_data)
    }
    header = {
        'User-Agent': 'Mozilla/5.0',
    }
    rsp_data = requests.post(url, post_data, files=files, headers=header, timeout=timeout)
    # rsp.ParseJsonRsp(rsp_data.text)
    return rsp_data.json()


class RC:
    # API接口调用类
    # 参数（appID，appKey，pdID，pdKey）
    def __init__(self, app_id, app_key, pd_id, pd_key):
        self.app_id = app_id
        if app_id is None:
            self.app_id = ""
        self.app_key = app_key
        self.pd_id = pd_id
        self.pd_key = pd_key
        self.host = FATEA_PRED_URL

    def SetHost(self, url):
        self.host = url

    def rk_create(self, img_data, pred_type, timeout=60, head_info=""):
        """
        识别验证码
        参数：pred_type:识别类型  img_data:图片的数据
        返回值：
          rsp.ret_code：正常返回0
          rsp.request_id：唯一订单号
          rsp.pred_rsp.value：识别结果
          rsp.err_msg：异常时返回异常详情
        """
        tm = str(int(time.time()))
        sign = CalcSign(self.pd_id, self.pd_key, tm)
        pred_type = int(pred_type) * 10
        param = {
            "user_id": self.pd_id,
            "timestamp": tm,
            "sign": sign,
            "predict_type": pred_type,
            "up_type": "mt"
        }
        if head_info is not None or head_info != "":
            param["head_info"] = head_info
        if self.app_id != "":
            #
            asign = CalcSign(self.app_id, self.app_key, tm)
            param["appid"] = self.app_id
            param["asign"] = asign
        url = self.host + "/api/capreg"
        files = img_data
        rsp = HttpRequest(url, param, files, timeout=timeout)
        if rsp.get('RetCode') == '0':
            rsp['Result'] = json.loads(rsp.pop('RspData')).get('result')
            print(rsp)
        else:
            rsp['Id'] = rsp.pop('RequestId')
        return rsp

    def rk_report_error(self, request_id):
        """
        识别失败，进行退款请求
        参数：request_id：需要退款的订单号
        返回值：
        rsp.ret_code：正常返回0
        rsp.err_msg：异常时返回异常详情

        注意:
        Predict识别接口，仅在ret_code == 0时才会进行扣款，才需要进行退款请求，否则无需进行退款操作
        注意2:
        退款仅在正常识别出结果后，无法通过网站验证的情况，请勿非法或者滥用，否则可能进行封号处理
        """
        if request_id == "":
            #
            return
        tm = str(int(time.time()))
        sign = CalcSign(self.pd_id, self.pd_key, tm)
        param = {
            "user_id": self.pd_id,
            "timestamp": tm,
            "sign": sign,
            "request_id": request_id
        }
        url = self.host + "/api/capjust"
        rsp = HttpRequest(url, param, timeout=60)
        print(rsp)
        return rsp

    def rk_report(self, im, im_type, vn, timeout=60):
        # very_str = f'verify_str_{time.strftime("%Y-%m-%d %H:%M")}'
        # vs = hashlib.md5(very_str.encode('utf-8')).hexdigest()
        # url = 'http://144.34.194.228/upImg/%s/%s/%s' % (im_type, vn, vs)
        # resp = requests.post(url, files={'image': ('%s.png' % vn, im)}, timeout=timeout)
        # print(resp.text)
        return


def TestFunc():
    pd_id = "111713"  # 用户中心页可以查询到pd信息
    pd_key = "NHScyK2S/lk4Ts1Eq6Y/IPsMYskmos3a"
    app_id = "311713"  # 开发者分成用的账号，在开发者中心可以查询到
    app_key = "M7Xcoec+myjJJ1puxOM38+3YnrH7QapW"
    # 识别类型，
    # 具体类型可以查看官方网站的价格页选择具体的类型，不清楚类型的，可以咨询客服
    pred_type = "30400"
    api = RC(app_id, app_key, pd_id, pd_key)
    # 查询余额
    # balance 		= api.QueryBalcExtend()   # 直接返余额
    # api.QueryBalc()

    # 通过文件形式识别：
    file_name = "img.jpg"
    # result =  api.PredictFromFileExtend(pred_type,file_name)   # 直接返回识别结果
    with open(file_name, 'br') as f:
        im = f.read()
    rsp = api.rk_create(im, pred_type)  # 返回详细识别结果


if __name__ == "__main__":
    TestFunc()
