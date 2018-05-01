import base64
import cv2
import matplotlib.pyplot as plt
import numpy as np
import pickle
import socket
import sys
import time

# constants
CONNECTIONS = 1
HOST = "localhost"
PORT = 8080
BUF_SIZE = 8192

# create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to port
server.bind((HOST, PORT))
# listen for incoming connections
server.listen(CONNECTIONS)

# create a named window
cv2.namedWindow("server")

result = []
width, height, channels = 0, 0, 0

state = 0

prev = 0

while True:
    print("--- waiting for a connection ---")
    client, client_address = server.accept()
    try:
        print("--- client from {} ---".format(client_address))
        while True:
            # print("--- getting data ---")
            # get image size and decode
            received = client.recv(BUF_SIZE)
            if received:
                # pass
                if state == 0:                    
                    temp = received.decode("utf-8")
                    temp = temp.split()
                    width = int(temp[1])
                    print("GOT WIDTH : {}".format(width))
                    state += 1
                elif state == 1:
                    temp = received.decode("utf-8")
                    temp = temp.split()
                    height = int(temp[1])
                    print("GOT HEIGHT : {}".format(height))
                    state += 1                                    
                else:
                    if received == b'end':
                        curr = time.time()
                        print("took {} time".format(1/abs(curr-prev)))
                        # print("NEW FRAME")
                        result_arr = pickle.loads(b"".join(result))
                        image = np.frombuffer(result_arr, dtype=np.uint8)
                        image = np.reshape(image, (height, width))
                        cv2.imshow("server", image)
                        # exit loop on "q" key
                        if cv2.waitKey(1) & 0xFF == ord("q"):
                            client.close()
                            quit(0)
                            break

                        # plt.imshow(image, cmap="gray")
                        # plt.show()
                        result = []
                        prev = time.time()
                        # quit(0)
                    else:
                        result.append(received)
            else:
                print("--- no more data from client ---")                                
                print(width)
                print(height)
                print(channels)
                break
    finally:
        client.close()
