import time
import SocketServer
from Queue import Queue
from threading import Thread
HOST = 'localhost'
PORT = 10001

# msq queues
q_recv = Queue(maxsize=0)
q_send = Queue(maxsize=0)

class EchoRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        # put msg in receive queue
        q_recv.put(self.request.recv(1024))
        # wait for something to send back
        while q_send.empty():
            time.sleep(1)
        # send it
        while not q_send.empty():
            reply = q_send.get()
            self.request.send(reply)
        return

SocketServer.TCPServer.allow_reuse_address = True
server = SocketServer.TCPServer((HOST, PORT), EchoRequestHandler)

worker = Thread(target=server.serve_forever)
worker.setDaemon(True)
worker.start()

loops = 0
cont = True
while cont == True:
    loops += 1

    time.sleep(1)
    while not q_recv.empty():
        msg = q_recv.get()
        msg = msg.strip()
        if msg == 'loops':
            q_send.put(str(loops))
        elif msg == 'end':
            q_send.put("finishing")
            cont = False;
        else:
            q_send.put("bad req")

