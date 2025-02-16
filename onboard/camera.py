import cv2
import socket
import struct
import pickle

HOST = ""
PORT = 5000

def run():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(5)
    while True:
        client, addr = sock.accept()
        print(f"Connection from {addr}")
        if client:
            vid = cv2.VideoCapture(0)
            while vid.isOpened():
                img, frame = vid.read()
                if not img:
                    break
                data = pickle.dumps(frame)
                size = len(data)
                client.sendall(struct.pack(">L", size) + data)

if __name__ == "__main__":
    run()
