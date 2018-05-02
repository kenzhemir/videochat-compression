import argparse
import base64
import cv2
import matplotlib.pyplot as plt
import numpy as np
import pickle
import socket
import sys
import time
from compressor import DecompressorYCC
from compressorTest import printRatio
import dithering

# argument parser
parser = argparse.ArgumentParser(
    description='Connect to a socket for video chat')
parser.add_argument(
    '--host', dest='hostname', help='Enter a server hostname', required=True)
parser.add_argument(
    '--port', dest='port', help='Enter a server port', required=True)
args = parser.parse_args()

# constants
CONNECTIONS = 1
HOST = args.hostname
PORT = int(args.port)
BUF_SIZE = 8192

# create decompressor
decomp = DecompressorYCC()

# create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to port
server.bind((HOST, PORT))
# listen for incoming connections
server.listen(CONNECTIONS)

# create a named window
cv2.namedWindow("server")

result = []
width, height, channels = 0, 0, 3

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

                    # set decomp shape
                    decomp.shape = (height, width, channels)
                else:
                    if received == b'end':
                        curr = time.time()
                        print("took {} time".format(1 / abs(curr - prev)))
                        # print("NEW FRAME")
                        result_arr = pickle.loads(b"".join(result))
                        image = np.frombuffer(result_arr, dtype=np.uint8)

                        decompressed2 = dithering.unpackTruncated(image)
                        decompressed1 = decomp.decompress(decompressed2)
                        printRatio(decompressed1, image)

                        # image = np.reshape(image, (height, width, channels))
                        image = decompressed1
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
