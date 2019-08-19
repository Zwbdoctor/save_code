

def startswith(data):
    for s in ['INFO', 'DEBUG', 'WARNING']:
        if not data.startswith(s):
            return False
    return True


def parse(log_name):
    f = open(log_name, 'r')
    while True:
        data = f.readline()
        # pass startswith debug,info,warning
        if startswith(data):
            continue
        # startswith ERROR
        # todo: send error msg
        # todo: data if startswith(info:start~end)

