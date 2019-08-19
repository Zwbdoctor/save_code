import os
imgs_path = os.path.join(os.path.abspath('.'), 'imgs\\wifi_imgs\\')
log_path = os.path.join(os.path.abspath('./logs'), 'wifi')
# js_path = os.path.join(os.path.abspath('./utils'), 'preload.js')


# img_dicts = [
#     {'img_name': 'user_name', 'img_path': imgs_path + r'\user_name.png', 'sleep_time': 1, 'location': None,
#      'input_data': 'wangdi@btomorrow.cn', 'need_current': False},
# ]
page_dict = {'url': 'http://ad.wifi.com/', 'log_path': log_path, 'pst': 3, 'log_file': 'wifi.log', 'imgs_path': imgs_path,
             'ret_data': {'startDate': None, 'account': "1969394232@qq.com", 'cookie': None, 'errorCode': 0,
                          'platform': 'wifikey', 'errMsg': '成功'},
             'passwd': 'HHabc123', 'host': 'ad.wifi.com', 'opera_type': 'driver',
             'delete_host_cookie': [
                 'ad.wifi.com',
             ]}
