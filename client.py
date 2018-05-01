import socket
import pickle
import numpy as np
import cv2
import matplotlib.pyplot as plt

# constants
BUF_SIZE = 4096
HOSTNAME = "localhost"
PORT = 8080

class ClientSocket:
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.socket.connect((self.hostname, self.port))

    def send(self, msg):
        print("Sending message to {}:{}".format(self.hostname, self.port))
        data = pickle.dumps(msg)
        self.socket.sendall(data)

    def receive(self, buf_size):
        print("Waiting to receive a message of {} bytes".format(buf_size))
        data = self.socket.recv(buf_size)
        msg = pickle.loads(data)
        return msg

    def close(self):
        self.socket.close()


# read image from defined path
image_path = "image.jpg"
image = cv2.imread(image_path)

# plt.imshow(image)
# plt.show()

# create an INET, STREAMing socket
socket = ClientSocket(HOSTNAME, PORT)
# now connect to the server on the defined port
socket.connect()

try:
    # send image shape
    sizemsg = "SIZE: {} {}".format(image.shape[0], image.shape[1])    
    sizemsg = pickle.dumps(sizemsg)
    socket.send(sizemsg)
    print("SENT SIZE TO SERVER")

    # receive answer
    answer = socket.receive(BUF_SIZE)
    answer = pickle.loads(answer)
    print("ANSWER FROM SERVER: {}".format(answer))

    if answer == "GOT SIZE":
        # send image
        print("NOW SENDING IMAGE TO SERVER")
        data = pickle.dumps(image)        
        sent = socket.send(data)
        print("SENT: {}".format(sent))

finally:
    # close socket
    socket.close()
