import cv2
import socket
import struct
import pickle

# HOST = "127.0.0.1" #FIXME
HOST = "" #FIXME
PORT = 5000 #FIXME

def run():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # receive camera frames as UDP so faster
    sock.bind((HOST, PORT))

    while True:
        data, addr = sock.recvfrom(1280 * 720 * 3) # size of image??? FIXME TODO

        img = pickle.loads(data)

        # cv2.imshow("Frame", img)

        #TODO image recognition ASL stuff (big)

        #TODO sock.send back to the addr we got with the character from the thingy

        #TODO ???????


if __name__ == "__main__":
    run()
