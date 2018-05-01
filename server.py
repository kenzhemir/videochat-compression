import socket
import select
import pickle
import struct
import threading
import numpy as np
import cv2

# constants
BUF_SIZE = 4096
HOSTNAME = "localhost"
PORT = 8080

class ServerSocket:
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, connections):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(connections)

    def accept(self):
        (client, address) = self.socket.accept()
        return (client, address)

    def receive(self, buf_size):
        return self.socket.recv(BUF_SIZE)



# create a server socket
server = ServerSocket(HOSTNAME, PORT)
# start a server socket with 1 connections
server.start(1)
# print messages
print("--- Started server at {}:{} ---".format(HOSTNAME, PORT))
print("--- Waiting for the client ---")
# accept a client; blocking call
(client, address) = server.accept()
# print message when client arrived
print("--- Got a client ---")

result = []
state = 0

# main loop
while True:
    try:
        print("--- Waiting for resource ---")
        resource = server.receive(BUF_SIZE)
        print("--- Got a response ---")
        # if empty response
        if resource == 0:
            print("--- Empty response ---")
            break
        
        if state == 0:
            try:
                data = pickle.loads(resource)
            except:
                print("--- Exception happened ---")

            if str(data).startswith("SIZE"):
                msg = data.split()
                shape = [int(msg[1]), int(msg[2])]
                size = shape[0]*shape[1]
                print("SHAPE: {}".format(shape))
                client.send(pickle.dumps("GOT SIZE"))
        else:
            pass
            # sborka baitov do saiza
        print("--- Data accepted ---")

        # if str(data).startswith("SIZE"):
        #     print("GOT SIZE ON SERVER")
        #     print(data)
        #     answer = "GOT SIZE"
        #     # answer = answer.encode("utf-8")
        #     answer = pickle.dumps(answer)
        #     clientsocket.sendall(answer)
            
        #     msg = data.split()
        #     shape = [int(msg[1]), int(msg[2])]
        #     print("SHAPE: {}".format(shape))            
        # elif resource:
        #     print("GOT IMAGE ON SERVER")
        #     print(data)
        #     result += data
            
    except KeyboardInterrupt:
        server.close()
        break

