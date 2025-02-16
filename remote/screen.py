import cv2
import socket
import pickle
import numpy as np
import asl

HOST = "0.0.0.0"
PORT = 5000

def receive():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
    sock.bind((HOST, PORT))
    
    while True:
        data, addr = sock.recvfrom(65536)
        frame_data = pickle.loads(data)
        frame = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)

        # flip the image vertically
        frame = np.flipud(frame)

        asl.on_image_received(frame)

        if cv2.waitKey(1) & 0xFF == ord("s"):
            print("Starting processing")
            asl.start()
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    
    sock.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    receive()