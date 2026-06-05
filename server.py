import socket

known_port = 50002

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

port = 12345

sock.bind(('0.0.0.0', port))


while True:
    clients = []
    usernames = []

    while True:
        username, address = sock.recvfrom(128)
        username = username.decode()
        print('connection from: {}'.format(address))
        clients.append(address)
        usernames.append(username)

        sock.sendto(b'ready', address)

        if len(clients) == 2:
            print('got 2 clients, sending details to each')
            break

    c1 = clients.pop()
    c1_addr, c1_port = c1
    c1User = usernames.pop()
    c2 = clients.pop()
    c2_addr, c2_port = c2
    c2User = usernames.pop()

    sock.sendto(f'{c1_addr}|{c1_port}|{known_port}|{c1User}'.encode(), c2)
    sock.sendto(f'{c2_addr}|{c2_port}|{known_port}|{c2User}'.encode(), c1)
