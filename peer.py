# imports
import argparse
import base64
import cv2
import numpy as np
import pickle
import socket
from threading import Thread
import time

# constants
SERVER_HOST = 'localhost'
# SERVER_PORT = 5000
CONNECTIONS = 1
BUF_SIZE = 8192

# auxiliary functions
def extract_shape(text):
    text = text.split()
    return int(text[1])

class ServerThread(Thread):
    def __init__(self, host, port, connections):
        Thread.__init__(self)
        # create a TCP/IP server socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind server socket to port
        self.server.bind((host, port))
        # listen for incoming connections
        self.server.listen(connections)
        # list for one frame
        self.peer_frame = []
        # tuple for frame shape
        self.peer_frame_shape = [0, 0, 0]
        # state variable
        self.state = 0
        # time variables
        self.prev = 0
        self.curr = 0

    def accept(self):
        # accept a client connection
        (self.client, self.client_address) = self.server.accept()

    def receive(self, buf_size):
        # receive a message from connected client
        self.received = self.client.recv(buf_size)

    def clear_frame(self):
        # clear peer frame list
        self.peer_frame = []

    def change_state(self):
        # change state
        self.state += 1

    def close(self):
        # close sockets
        self.client.close()
        self.server.close()        
        # destroy all CV windows
        cv2.destroyAllWindows()

    def run(self):
        # create named windows
        cv2.namedWindow('peer_stream')
        # accept a client connection
        print('--- waiting for a connection ---')
        self.accept()        
        while True:            
            # client stream routing
            try:
                # receive message from client
                self.receive(BUF_SIZE)
                # check if not empty
                if self.received:
                    if self.state == 0:
                        width = self.received.decode('utf-8')
                        width = extract_shape(width)
                        self.peer_frame_shape[0] = width
                        self.change_state()
                    elif self.state == 1:
                        height = self.received.decode('utf-8')
                        height = extract_shape(height)
                        self.peer_frame_shape[1] = height
                        self.change_state()
                    elif self.state == 2:
                        channels = self.received.decode('utf-8')
                        channels = extract_shape(channels)
                        self.peer_frame_shape[2] = channels
                        self.change_state()
                    else:
                        if self.received == b'end':
                            # calculate FPS
                            self.curr = time.time()
                            print('took {} time'.format(1/abs(self.curr - self.prev)))
                            # get peer frame
                            peer_frame_arr = pickle.loads(b"".join(self.peer_frame))
                            image = np.frombuffer(tuple(peer_frame_arr), dtype=np.uint8)
                            image = np.reshape(image, self.peer_frame_shape)
                            # show peer frame
                            cv2.imshow('peer_stream', image)
                            # exit loop on "q" key
                            key = cv2.waitKey(1) & 0xFF
                            if key == ord("q"):                                
                                self.close()
                                break
                            # clear peer frame
                            self.clear_frame()
                            # time frame receiving
                            self.prev = time.time()
                        else:
                            self.peer_frame(self.received)
                else:
                    self.close()
                    break
            finally:
                self.close()
                break


class PeerThread(Thread):
    def __init__(self, host, port):
        Thread.__init__(self)
        # create a TCP/IP peer socket
        self.peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # peer hostname and port
        self.peer_host = host
        self.peer_port = port        

    def connect(self):
        # connect to peer
        self.peer.connect(self.peer_host, self.peer_port)
        
    def send(self, msg):
        self.peer.sendall(msg)

    def capture_video(self):
        # create a capture from webcam
        self.cap = cv2.VideoCapture(0)

    def show_frame(self):
        # capture frame-by-frame
        self.ret, self.frame = self.cap.read()
        cv2.imshow('my_stream', self.frame)

    def close(self):
        # close sockets
        self.peer.close()        
        # release the webcam
        self.cap.release()
        # destroy all CV windows
        cv2.destroyAllWindows()

    def run(self):        
        # create named window
        cv2.namedWindow('my_stream')
        # start video capture
        self.capture_video()
        print('capturing video')
        # connect to peer
        self.connect()
        print('connected')
        # main loop
        while True:
            # show frame
            self.show_frame()
            # send frame routing
            try:
                # serialize frame
                data = pickle.dumps(self.frame)
                # send serialized frame
                self.send(data)
                # send end message
                end_message = 'end'.encode('utf-8')
                self.send(end_message)
            except:
                self.close()
                break
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.close()
                break

# argument parser
parser = argparse.ArgumentParser(description='Connect to a socket for video chat')
parser.add_argument('--server-port', dest='server_port', help='Enter a server port', required=True)
parser.add_argument('--host', dest='hostname', help='Enter a peer hostname', required=True)
parser.add_argument('--port', dest='port', help='Enter a peer port', required=True)
args = parser.parse_args()

# run from command line
if __name__ == '__main__':
    print('Starting server thread')
    server_thread = ServerThread(SERVER_HOST, int(args.server_port), CONNECTIONS)
    server_thread.start()

    print('Press Enter when peer server is ready')
    input()

    print('Starting peer thread')
    peer_thread = PeerThread(args.hostname, args.port)
    peer_thread.start()