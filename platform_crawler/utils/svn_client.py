import socket


# ##### Client #####
def client(addr='127.0.0.1'):
    sock = socket.socket()
    sock.connect((addr, 8889))
    while True:
        recv_msg = sock.recv(1024)
        print(f'>>:{recv_msg.decode()}')
        send_msg = input('<<:')
        if send_msg == '0':
            sock.sendall(send_msg.encode())
            recv_msg = sock.recv(1024)
            print(f'>>:{recv_msg.decode()}')
            sock.close()
            break
        sock.sendall(send_msg.encode())
    print('disconnect from the server')


def cli_menu():
    cpa = '192.168.0.121'
    msg = '192.168.0.119'
    msg2 = '192.168.0.106'
    client_maps = {'cpa': cpa, 'msg': msg, 'msg2': msg2, 'default': '127.0.0.1'}
    recent = []
    recent_msg = ''
    while True:
        inp_data = input(f'Please choose one of the client to connect:\n{client_maps.keys()}, '
                         f'or press any key to exit\n{recent_msg  if recent else ""}>>:').strip()
        if inp_data in client_maps.keys():
            client(client_maps.get(inp_data))
            recent.append(inp_data)
            recent_msg = f'recent action: {recent}\n'
        else:
            print('input not in the choice, exit')
            break


if __name__ == '__main__':
    cli_menu()
