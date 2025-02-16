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
    vid = cv2.VideoCapture(0)
    while True:
        client, addr = sock.accept()
        print(f"Connection from {addr}")
        if client:
            vid.set(3, 1280)
            vid.set(4, 720)
            while vid.isOpened():
                img, frame = vid.read()
                if not img:
                    print("No image.")
                    break
                data = pickle.dumps(frame)
                client.sendall(struct.pack("Q", len(data) + data))
    

if __name__ == "__main__":
    run()
