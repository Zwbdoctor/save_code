import os
imgs_path = os.path.join(os.path.abspath('./imgs'), 'app_imgs\\')
log_path = os.path.join(os.path.abspath('./logs'), 'app')


img_dicts = {
    'username': imgs_path + 'username.png', 'password': imgs_path + 'password.png',
    'entrance': imgs_path + 'to_login.png', 'login_way': imgs_path + 'choose_login_way.png',
    'click_login': imgs_path + 'login_btn.png',
    'vc_path': imgs_path + 'verifyCode.png',
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
