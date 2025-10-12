import psutil
from tkinter import messagebox

def is_program_running(program_name):
    """
    Checks if a program with the given name is currently running.
    program_name can be the exact executable name (e.g., "chrome.exe", "python")
    or a part of the command line for more specific identification (e.g., "my_script.py").
    """
    for process in psutil.process_iter(['name', 'cmdline']):
        try:
            # Check by process name
            if process.info['name'] and program_name.lower() in process.info['name'].lower():
                return True
            # Check by command line arguments for more specific identification
            if process.info['cmdline'] and any(program_name.lower() in arg.lower() for arg in process.info['cmdline']):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

if is_program_running("RobloxPlayerBeta.exe"):
    messagebox.showinfo("Message", "Can I uninstall Roblox Ele? You can get it on your phone. - Isaias")