import socket
import numpy as np
import cv2

# put hostname
HOST = ""
PORT = 8080

# read image from defined path
image_path = ""
image = cv2.imread(image_path)

# create an INET, STREAMing socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# now connect to the server on the defined port
s.connect((HOST, PORT))

# send image through the socket
s.send(bytes(image))
