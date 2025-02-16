import subprocess
import threading

def run():
    script_names = ["image_processing.py"]
    threads = []
    for script in script_names:
        thread = threading.Thread(target=subprocess.run, args=(["python", script],))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    run()