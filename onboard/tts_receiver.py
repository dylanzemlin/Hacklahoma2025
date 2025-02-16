import pyttsx3
import socket


engine = pyttsx3.init()
engine.setProperty("rate", 140)
engine.setProperty("volume", 1.0)

voices = engine.getProperty('voices') 
engine.setProperty('voice', voices[1].id)

HOST = "127.0.0.1"
PORT = 5004

def speak(text):
    engine.say(text)
    engine.runAndWait()

def main():
    # listen on the udp port and speak any received text
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        while True:
            data, addr = s.recvfrom(1024)
            text = data.decode("utf-8")
            print(f"Received: {text}")
            speak(text)

if __name__ == "__main__":
    main()