import cv2
import socket
import struct

UDP_IP = ""
UDP_PORT = 5005

def run():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
    
    _, encoded_frame = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
    data = encoded_frame.tobytes()

    max_packet_size = 65000
    num_packets = (len(data) // max_packet_size) + 1

    for i in range(num_packets):
        start = i * max_packet_size
        end = start + max_packet_size
        fragment = data[start:end]
        packet_header = struct.pack("B", i)
        sock.sendto(packet_header + fragment, (UDP_IP, UDP_PORT))

    cap.release()
    sock.close()

if "__name__" == "__main__":
    run()
