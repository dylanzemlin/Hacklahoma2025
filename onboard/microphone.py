import socket
import speech_recognition as sr
import time

TCP_IP = ""
TCP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((TCP_IP, TCP_PORT))
type_message = "MICROPHONE"
sock.sendall(type_message.encode())

def record_callback(_, audio:sr.AudioData):
    global sock

def run():
    recorder = sr.Recognizer()
    recorder.energy_threshold = 3200
    source = sr.Microphone(sample_rate=16000)
    with source:
        recorder.adjust_for_ambient_noise(source, duration=3)
    
    recorder.listen_in_background(source, record_callback, phrase_time_limit=5)


if "__name__" == "__main__":
    run()