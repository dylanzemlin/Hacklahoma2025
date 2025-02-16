import socket
import cv2

serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serversocket.bind(("", 5000))

while True:
    x = serversocket.recv(65536)

    print(x)

    cv2.Mat(x)

    cv2.imshow("Frame", x)

    raise SystemExit