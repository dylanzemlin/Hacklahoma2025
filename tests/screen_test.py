import socket
import time

server_ip = "127.0.0.1" 
server_port = 8080

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_message(message):
    """Send a message over UDP to the server."""
    try:
        sock.sendto(message.encode(), (server_ip, server_port))
        print(f"Sent: {message}")
    except Exception as e:
        print(f"Error sending message: {e}")

def main():
    test_messages = ['Hello', ' ', 'World', '!', ' ', 'This', ' ', 'is', ' ', 'a', ' ', 'test', '.']
    
    for msg in test_messages:
        for char in msg:
            send_message(char)
            time.sleep(0.1)

    sock.close()

if __name__ == "__main__":
    main()
