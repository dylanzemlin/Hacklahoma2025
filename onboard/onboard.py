import subprocess
import threading

def run():
    script_names = ["camera.py", "firmware/screen.cpp"]
    threads = []
    for script in script_names:
        if script.endswith(".py"):
            thread = threading.Thread(target=subprocess.run, args=(["python", script],))
        elif script.endswith(".cpp"):
            thread = threading.Thread(target=subprocess.run, args=(["g++", script, "-o", "screen", "&&", "./screen"],))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    run()