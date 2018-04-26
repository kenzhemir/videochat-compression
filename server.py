import socket
import threading
import numpy as np

BUF_SIZE = 4096
host = ""
port = 8080

# create an INET, STREAMing socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a public host, and a well-known port
serversocket.bind((host, port))
# become a server socket
serversocket.listen(5)
print("Started server at {}:{}".format(host, port))

(clientsocket, address) = serversocket.accept()

print("Client came")
while True:
    try:
        # accept connections from outside
        # now do something with the clientsocket
        # in this case, we'll pretend this is a threaded server
        print("Waiting for resource")
        resource = clientsocket.recv(BUF_SIZE)
        if resource == bytes(0):
            break
        print("Resource accepted")
        print(len(resource))
    except KeyboardInterrupt:
        serversocket.close()
        break
