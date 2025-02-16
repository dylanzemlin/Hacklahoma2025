import pyttsx3

engine = pyttsx3.init()
engine.setProperty("rate", 120)
engine.setProperty("volume", 1.0)

def speak(text):
    engine.say(text)
    engine.runAndWait()