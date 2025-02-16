import pyttsx3

engine = pyttsx3.init()
engine.setProperty("rate", 120)
engine.setProperty("volume", 1.0)

voices = engine.getProperty('voices') 
engine.setProperty('voice', voices[1].id)

def speak(text):
    engine.say(text)
    engine.runAndWait()