import base64
import cv2
import pickle
import socket
import sys
import time

# constants
IMAGE_PATH = "image.jpg"
HOST = "localhost"
PORT = 8080
BUF_SIZE = 8192

# create a TCP/IP socket
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# connect the socket to server
socket.connect((HOST, PORT))

# create a named window
cv2.namedWindow("frame")
# create a capture from webcam
cap = cv2.VideoCapture(0)

# get frame sizes
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
# send sizes to server
width_message = "width: {}".format(int(width)).encode("utf-8")
height_message = "height: {}".format(int(height)).encode("utf-8")
print(width_message, height_message)
# width_message = pickle.dumps(width_message)
# height_message = pickle.dumps(height_message)

socket.sendall(width_message)
time.sleep(0.1)
socket.sendall(height_message)

# camera loop
while True:
    # capture frame-by-frame
    ret, frame = cap.read()
    # convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # display the frame
    cv2.imshow("frame", gray)
    try:
        # sending frame through socket
        data = pickle.dumps(gray)
        socket.sendall(data)
        # time.sleep(0.01)
        socket.sendall("end".encode("utf-8"))
    except:
        print("exception")
        break
    # exit loop on "q" key
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# close the socket
socket.close()
# release the webcam
cap.release()
cv2.destroyAllWindows()    