import socket
import time

# Define server IP and port
server_ip = "127.0.0.1"  # Replace with the IP address of your Raspberry Pi or server
server_port = 8080

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_message(message):
    """Send a message over UDP to the server."""
    try:
        # Send the message to the server
        sock.sendto(message.encode(), (server_ip, server_port))
        print(f"Sent: {message}")
    except Exception as e:
        print(f"Error sending message: {e}")

def main():
    # Test sending some characters to see the display update
    test_messages = ['H', 'e', 'l', 'l', 'o', '\n', 'W', 'o', 'r', 'l', 'd', '!', ' ']
    
    for msg in test_messages:
        send_message(msg)
        time.sleep(1)  # Wait for the display to update
    
    # Close the socket
    sock.close()

if __name__ == "__main__":
    main()
