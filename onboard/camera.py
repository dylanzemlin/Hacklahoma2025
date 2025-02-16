import cv2
import socket
import pickle

HOST = "127.0.0.1"
PORT = 5000

def run():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # modify the SOL_SOCKET (socket-level) setting of SO_RCVBUF (receive buffer size) to 65536,
    # because we are sending images and images are big
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536) 
    sock.connect((HOST, PORT))
    # sock.bind((HOST, 5000))
    
    vid = cv2.VideoCapture(0)

    while True:
        vid.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        while vid.isOpened():
            img, frame = vid.read()

            if not img:
                print("No image.")
                break

            _, encoded = cv2.imencode(".jpg", frame, (cv2.IMWRITE_JPEG_QUALITY, 80, cv2.IMWRITE_JPEG_OPTIMIZE, 1))
            sock.sendto(pickle.dumps(encoded), (HOST, PORT))
    

if __name__ == "__main__":
    run()
