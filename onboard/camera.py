import cv2
import socket
import struct
import pickle

HOST = ""
PORT = 5000

def run():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    # sock.listen(5)
    vid = cv2.VideoCapture(0)

    while True:
        vid.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        while vid.isOpened():
            img, frame = vid.read()
            if not img:
                print("No image.")
                break
            data = pickle.dumps(frame)
            # sock.sendall(struct.pack("Q", len(data) + data))
            sock.sendto(data, ("127.0.0.1", 5000))
    

if __name__ == "__main__":
    run()
