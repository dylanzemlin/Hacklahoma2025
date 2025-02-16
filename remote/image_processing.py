import cv2
import socket
import pickle

HOST = "127.0.0.1"
PORT = 5000

def receive():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
    sock.bind((HOST, PORT))
    
    while True:
        data, addr = sock.recvfrom(65536)
        frame_data = pickle.loads(data)
        frame = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)
        cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    
    sock.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    receive()