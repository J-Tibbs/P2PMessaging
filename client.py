import socket
import sys
import threading
import datetime
import os
from pathlib import Path

directory_name = Path('previous_messages')
directory_name.mkdir(exist_ok=True)

# Create directory
try:
    os.mkdir(directory_name)
except FileExistsError:
    pass


username = input("What is your username: ")


#Change to current IP
rendezvous = ('', 12345)

# Create written file
filename = f"messages.{datetime.datetime.now().strftime('%d-%m-%Y')}"
filepath = directory_name / filename

filepath.touch(exist_ok=True)

def connect(username):

    print('connecting to rendezvous server')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 50001))
    sock.sendto(username.encode(), rendezvous)

    while True:
        data = sock.recv(1024).decode()

        if data.strip() == 'ready':
            print('checked in with the server, waiting')
            break

    data = sock.recv(1024).decode()
    ip, sport, dport, pUser = data.split('|')
    sport = int(sport)
    dport = int(dport)
    
    sock.close()

    return ip, sport, dport, pUser

def reconnect(username):
    global ip, sport, dport, pUser
    ip, sport, dport, pUser = connect(username)

ip, sport, dport, pUser = connect(username)

print('\ngot peer')
print('     ip:     {}'.format(ip))
print('     source port:     {}'.format(sport))
print('     dest port:     {}'.format(dport))

print('punching hole')

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.sendto(b'0', (ip, dport))

print('ready to echange messages\n')


def writeDown(filepath, message, username):
    with open(filepath, 'a') as file:
        file.write(datetime.datetime.now().strftime("%I:%M:%S") + " | " + username + ": " + message + "\n")


def listen():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', sport))



    while True:
        data = sock.recv(1024)

        if data == b'__DISCONNECT__':
            print(f'\n{pUser} has disconnected.')
            writeDown(filepath, f'{pUser} has disconnected.', '>>>')
            sock.close()
            print("Reconnecting...")
            reconnect(username)
            break
        else:
            print(f'\r{pUser}: {data.decode()}\n', end='')
            writeDown(filepath, data.decode(), pUser)


listener = threading.Thread(target = listen, daemon = True)
listener.start()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', dport))


    
try:
    while True: 
        msg = input('> ')
        sock.sendto(msg.encode(), (ip, sport))
        writeDown(filepath, msg, username) 
except KeyboardInterrupt:
    sock.sendto(b'__DISCONNECT__', (ip, sport))
    print("Disconnecting...")
    writeDown(filepath, f"{username} disconnected", '>>>')
