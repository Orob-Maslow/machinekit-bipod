#!/usr/bin/python
import socket
import argparse

HOST = 'localhost'
PORT = 10001

def send(cmd):
    # Connect to the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setblocking(True)
    s.settimeout(2)
    s.connect((HOST, PORT))

    len_sent = s.send(cmd)

    # Receive a response
    response = s.recv(1024)
    print('received [%s]' % response)

    # Clean up
    s.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="control bipod process")
    parser.add_argument('--start',
        action='store_const', const=True)
    parser.add_argument('--quit',
        action='store_const', const=True)
    parser.add_argument('--skip',
        action='store_const', const=True)
    parser.add_argument('--programs',
        action='store_const', const=True)
    parser.add_argument('--halt',
        action='store_const', const=True)

    args = parser.parse_args()

    # Send the message
    if args.start:
        send('start')
    elif args.quit:
        send('quit')
    elif args.skip:
        send('skip')
    elif args.programs:
        send('programs')
    elif args.halt:
        send('halt')

