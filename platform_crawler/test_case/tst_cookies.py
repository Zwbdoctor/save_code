import json
import requests
from requests.utils import quote

url = "http://feedads.baidu.com/nirvana/request.ajax"

querystring = {"path":"pluto/GET/mars/reportdata"}

# payload = "userid=24575016&token=51adf2a18e90e7d7842c00034032b0ebf487dcf9baca4e9814b44ff2b994c88775052dcc564935a1cef84748&path=pluto%2FGET%2Fmars%2Freportdata&params=%7B%22pageSize%22%3A20%2C%22pageNo%22%3A1%2C%22maxRecordNum%22%3A0%2C%22reportinfo%22%3A%7B%22reportid%22%3A0%2C%22starttime%22%3A%222019-06-01%22%2C%22endtime%22%3A%222019-06-30%22%2C%22isrelativetime%22%3A0%2C%22relativetime%22%3A14%2C%22mtldim%22%3A2%2C%22idset%22%3A24575016%2C%22mtllevel%22%3A200%2C%22platform%22%3A23%2C%22reporttype%22%3A700%2C%22splitDim%22%3A%22%22%2C%22filter%22%3Anull%2C%22dataitem%22%3A%22date%2Cuseracct%2Cpaysum%2Cshows%2Cclks%2Cclkrate%2Cavgprice%2Cshowpay%2Cmmpv%2Ctrans%22%2C%22reporttag%22%3A0%2C%22reportcycle%22%3A1%2C%22timedim%22%3A7%2C%22firstday%22%3A1%2C%22ismail%22%3A0%2C%22mailaddr%22%3A%22%22%2C%22sortlist%22%3A%22date%20DESC%22%2C%22reportname%22%3A%22%E4%BF%A1%E6%81%AF%E6%B5%81%E6%8E%A8%E5%B9%BF%E8%B4%A6%E6%88%B7%E6%8A%A5%E5%91%8A%22%2C%22userid%22%3A24575016%2C%22reportlevel%22%3A100%2C%22rgtag%22%3Anull%2C%22mtag%22%3Anull%2C%22feedSubject%22%3A%22%22%2C%22bstype%22%3A%22%22%7D%7D"
pdata = {
    "userid": '24575016',
    "token": '51adf2a18e90e7d7842c00034032b0ebf487dcf9baca4e9814b44ff2b994c88775052dcc564935a1cef84748',
    "path": quote("pluto/GET/mars/reportdata", safe=''),
    "params": quote(json.dumps({"pageSize": 50, "pageNo": 1, "maxRecordNum": 0,
                                "reportinfo": {"reportid": 0, "starttime": '2019-06-02', "endtime": '2019-06-21', "isrelativetime": 0,
                                               "relativetime": 14, "mtldim": 2, "idset": '24575016', "mtllevel": 200,
                                               "platform": 23, "reporttype": 700, "splitDim": "", "filter": None,
                                               "dataitem": "date,useracct,paysum,shows,clks,clkrate,avgprice,showpay,mmpv,trans",
                                               "reporttag": 0, "reportcycle": 1, "timedim": 7, "firstday": 1,
                                               "ismail": 0, "mailaddr": "", "sortlist": "date DESC",
                                               "reportname": "信息流推广账户报告", "userid": '24575016', "reportlevel": 100,
                                               "rgtag": None, "mtag": None, "feedSubject": "", "bstype": ""}}))
}
pdata = '&'.join('%s=%s' % (k, v) for k, v in pdata.items())
headers = {
    'Accept': "*/*",
    'Content-Type': "application/x-www-form-urlencoded",
    'Cookie': "FC-FE-TERMINUS=fc_terminus_user; FC-FE-EDEN=fc_eden_user; BAIDUID=BDEA5E3A0CBFE6ADF246BAC221F37103:FG=1; SIGNIN_UC=70a2711cf1d3d9b1a82d2f87d633bd8a03133692222; uc_login_unique=32f75ea2ede43d65f372e3a0b52a3183; uc_recom_mark=cmVjb21tYXJrXzI0NTc1MDE2; Hm_lvt_77c8f01bd6e840e4b9972122fd60c05e=1563357111; __cas__rn__=313369222; __cas__st__3=51adf2a18e90e7d7842c00034032b0ebf487dcf9baca4e9814b44ff2b994c88775052dcc564935a1cef84748; __cas__id__3=24575016; CPTK_3=1511674410; CPID_3=24575016; Hm_lpvt_77c8f01bd6e840e4b9972122fd60c05e=1563357112; AGL_USER_ID=19a82a14-385b-4f07-a073-c8517b6582f2,FC-FE-TERMINUS=fc_terminus_user; FC-FE-EDEN=fc_eden_user; BAIDUID=BDEA5E3A0CBFE6ADF246BAC221F37103:FG=1; SIGNIN_UC=70a2711cf1d3d9b1a82d2f87d633bd8a03133692222; uc_login_unique=32f75ea2ede43d65f372e3a0b52a3183; uc_recom_mark=cmVjb21tYXJrXzI0NTc1MDE2; Hm_lvt_77c8f01bd6e840e4b9972122fd60c05e=1563357111; __cas__rn__=313369222; __cas__st__3=51adf2a18e90e7d7842c00034032b0ebf487dcf9baca4e9814b44ff2b994c88775052dcc564935a1cef84748; __cas__id__3=24575016; CPTK_3=1511674410; CPID_3=24575016; Hm_lpvt_77c8f01bd6e840e4b9972122fd60c05e=1563357112; AGL_USER_ID=19a82a14-385b-4f07-a073-c8517b6582f2; BAIDUID=5C22307C7B4DB73D47CF00B9E2F5B76B:FG=1",
    'Host': "feedads.baidu.com",
    'Referer': "http://feedads.baidu.com/nirvana/main.html?userid=24575016",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
    'Connection': "keep-alive",
    'cache-control': "no-cache"
    }

response = requests.post(url, data=pdata, headers=headers, params=querystring)

print(response.text)
