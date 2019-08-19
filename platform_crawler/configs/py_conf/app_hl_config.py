import os
imgs_path = os.path.join(os.path.abspath('./imgs'), 'app_hl\\')
log_path = os.path.join(os.path.abspath('./logs'), 'app_hl')


img_dicts = {
    'vc_path': imgs_path + 'verifyCode.png', 'close_data_win': imgs_path + 'close_data_win.png'
}


page_dict = {'url': 'https://e.qq.com/ads/', 'log_path': log_path, 'pst': 3, 'log_file': 'app.log', 'imgs_path': imgs_path,
             'host': [
                 '.ptlogin2.qq.com', '.qq.com', 'xui.ptlogin2.qq.com', '.qidian.qq.com', '.e.qq.com', '.webpage.qidian.qq.com',
                 'e.qq.com', 'chat.qidian.qq.com'
             ],
             'delete_host_cookie': [
                 '.ptlogin2.qq.com', '.qq.com', 'xui.ptlogin2.qq.com', '.qidian.qq.com', '.e.qq.com', '.webpage.qidian.qq.com',
                 'e.qq.com', 'chat.qidian.qq.com'
             ]}
