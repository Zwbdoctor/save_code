# from pexpect import spawn, EOF
import pexpect
# import os
# from time import strftime


class Transfer:

    def __init__(self, ip, user, passwd):
        self.ip = ip
        self.user = user
        self.passwd = passwd
        print('Transfer working...')

    def transfer(self, dst_path, source_files, port, is_dir=False):
        passwd_key = '.*asword.*'
        if is_dir:
            cmd_line = 'scp -r %s %s@%s:%s' % (source_files, self.user, self.ip, dst_path)
        else:
            cmd_line = 'scp -P %s %s %s@%s:%s' % (port, source_files, self.user, self.ip, dst_path)
        try:
            child = pexpect.spawn(cmd_line)
            child.expect(passwd_key)
            child.sendline(self.passwd)
            child.expect(pexpect.EOF)
            print('Transfer work finished!')
        except Exception as e:
            print('upload failed')
            print(e)


def upload(local_path, dst_path, host, pwd, port):
    t2 = Transfer(host, 'root', pwd)
    return t2.transfer(dst_path, local_path, port)


def send_files():
    local_files = '/root/data.tar'
    dst_path = '/data/'
    import csv
    with open('./qq.xls', 'r', encoding='utf-8') as c:
        reader = csv.reader(c)
        hosts_data = list(reader)
    for data in hosts_data:
        host, pwd, port = data[4], data[7], data[5]
        upload(local_files, dst_path, host, pwd, port)


if __name__ == '__main__':
    send_files()



