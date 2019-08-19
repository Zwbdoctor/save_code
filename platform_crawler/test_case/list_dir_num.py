import os


def write_files():
    for i in range(10000):
        with open('./num_files/b%s.txt' % i, 'w') as f:
            f.write(str(i) + '  __abc')


def get_file_num():
    fs = os.listdir('./num_files')
    print(len(fs))


# write_files()
get_file_num()
