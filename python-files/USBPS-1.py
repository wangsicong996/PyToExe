import tkinter as tk
import subprocess
import sys
import os
import webbrowser
import random
import string
import smtplib
import cv2
import time
import datetime
import getpass
import sqlite3
import ctypes
import re
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
from email.message import EmailMessage


SENDER_EMAIL = "usb.phy.sec@gmail.com"
APP_PASSWORD = "fhra cpol iboc ulbw"
MASTER_PASSWORD = "your_secret_password"
current_generated_password = ""
log_file_path = 'event_log.txt'


def log_event(action, email=None):
    username = getpass.getuser()
    now = datetime.datetime.now()
    date_str = now.strftime("%d/%m/%Y")
    time_str = now.strftime("%H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO logs (date, time, username, action, email)
        VALUES (?, ?, ?, ?, ?)
    ''', (date_str, time_str, username, action, email))
    conn.commit()
    conn.close()

    
def log_event(action, email=None):
    """Log USB events to a text file in DD/MM/YYYY format with action, user, and optional email."""
    username = getpass.getuser()
    now = datetime.datetime.now()
    date_str = now.strftime("%d/%m/%Y")
    time_str = now.strftime("%H:%M:%S")
    with open(log_file_path, "a") as log_file:
        log_file.write(f"{date_str} | {time_str} | Action: {action} | User: {username}")
        if email:
            log_file.write(f" | Email: {email}")
        log_file.write("\n")


def record_intruder_video(filename="intruder.avi", duration=30):
    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))
    start_time = time.time()
    while int(time.time() - start_time) < duration:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
        else:
            break
    cap.release()
    out.release()


def resource_path(relative_path):
    """Get absolute path to a resource (works for dev and PyInstaller app)."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)




def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(random.choice(characters) for _ in range(length))
        if (any(c.islower() for c in password) and
            any(c.isupper() for c in password) and
            any(c.isdigit() for c in password) and
            any(c in string.punctuation for c in password)):
            return password


def invalidate_generated_password():
    global current_generated_password
    current_generated_password = ""


def send_password():
    recipient = email_entry.get().strip()
    if not is_valid_email(recipient):
        messagebox.showerror("Error", "Invalid email address format.")
        return

    global current_generated_password
    generated_pw = generate_password()
    current_generated_password = generated_pw

    try:
        msg = EmailMessage()
        msg['Subject'] = 'Your Secure Generated Password'
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient
        msg.set_content(f"Your new password is:\n\n{generated_pw}")

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, APP_PASSWORD)
            smtp.send_message(msg)

        log_event(f"Password sent to {recipient}")
        messagebox.showinfo("Success", f"Password sent to {recipient}")
    
    except smtplib.SMTPException as e:
        log_event(f"Email sending failed: {e}")
        messagebox.showerror("Email Error", f"Failed to send email: {e}")

    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        username = getpass.getuser()
        c.execute("SELECT * FROM users WHERE email = ?", (recipient,))
        if not c.fetchone():
            c.execute("INSERT INTO users (username, email, role) VALUES (?, ?, ?)", (username, recipient, 'local'))
            log_event(f"New user added to database: {username} ({recipient})")
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        log_event(f"Database error: {e}")
        messagebox.showerror("Database Error", f"Failed to save user: {e}")


def toggle_usb(enable=True):
    value = '3' if enable else '4'
    cmd = f'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\USBSTOR" /v "Start" /t REG_DWORD /d {value} /f'
    try:
        result = subprocess.run(cmd, shell=True)
        return result.returncode == 0
    except Exception as e:
        log_event(f"USB toggle failed: {str(e)}")
        messagebox.showerror("Error", "Unable to toggle USB.")
        return False


def show_password_prompt(enable):
    password_window = tk.Toplevel(root)
    password_window.title("Enter Password")
    password_window.geometry("300x200")
    password_window.configure(bg="#ffffff")

    password_label = tk.Label(password_window, text="Enter Password:", bg="#ffffff")
    password_label.pack(pady=10)

    password_entry = tk.Entry(password_window, show="*")
    password_entry.pack(pady=5)

    error_label = tk.Label(password_window, text="", font=("OCR A Extended", 12), fg="#ff0000", bg="#ffffff")
    error_label.pack()

    def ok_button():
        entered_pw = password_entry.get()
        global current_generated_password
        if entered_pw == MASTER_PASSWORD or (entered_pw == current_generated_password and current_generated_password != ""):
            if toggle_usb(enable):
                action = "USB Ports Enabled" if enable else "USB Ports Disabled"
                success_label.config(text=f"{action} Successfully", fg="#008000")
                log_event(action)
                password_window.destroy()
                invalidate_generated_password()
            else:
                 messagebox.showerror("Error", "Failed to toggle USB. Please run as administrator.")
            log_event("USB toggle failed due to permissions.")
        else:
            error_label.config(text="Incorrect password.\nPlease try again.")
            password_entry.delete(0, tk.END)
            record_intruder_video()

    tk.Button(password_window, text="OK", command=ok_button, bg="#4CAF50", fg="white", font=("OCR A Extended", 10, "bold")).pack(pady=10)


def on_enter(e, btn):
    btn['background'] = '#555555'


def on_leave(e, btn):
    btn['background'] = btn.default_bg


def initialize_user_database():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT NOT NULL,
                    email TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('admin', 'local'))
                )''')
    conn.commit()
    conn.close()


def show_user_database():
    def verify_password():
        if password_entry.get() == "P@ssw0rd!!":
            password_window.destroy()
            open_user_database()
        else:
            messagebox.showerror("Access Denied", "Incorrect password.")

    password_window = tk.Toplevel(root)
    password_window.title("Enter Password")
    password_window.geometry("300x150")
    password_window.configure(bg="white")

    tk.Label(password_window, text="Enter Password\nto Access Database", font=("OCR A Extended", 10), bg="white").pack(pady=10)
    password_entry = tk.Entry(password_window, show="*", font=("OCR A Extended", 10))
    password_entry.pack(pady=5)

    tk.Button(password_window, text="Submit", command=verify_password, font=("OCR A Extended", 10, "bold"), bg="black", fg="white").pack(pady=10)


def open_user_database():
    user_window = tk.Toplevel(root)
    user_window.title("Registered Users")
    user_window.geometry("600x400")
    user_window.configure(bg="#f0f0f0")

    title = tk.Label(user_window, text="User Database", font=("OCR A Extended", 16, "bold"), bg="#f0f0f0")
    title.pack(pady=10)

    tree = ttk.Treeview(user_window, columns=("username", "email", "role"), show='headings')
    tree.heading("username", text="Username")
    tree.heading("email", text="Email")
    tree.heading("role", text="Role")
    tree.column("username", width=150)
    tree.column("email", width=250)
    tree.column("role", width=100)
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT username, email, role FROM users")
    users = c.fetchall()
    conn.close()

    for user in users:
        tree.insert('', tk.END, values=user)


def view_status_clicked():
    username = getpass.getuser()
    latest_status = None

    if not os.path.exists(log_file_path):
        messagebox.showinfo("Status", "No log records found.")
        return
    
    with open(log_file_path, "r") as f:
        lines = f.readlines()
        for line in reversed(lines):
            if f"User: {username}" in line:
                if "USB Ports Enabled" in line:
                    latest_status = "Enabled"
                    break
                elif "USB Ports Disabled" in line:
                    latest_status = "Disabled"
                    break

    if not latest_status:
        messagebox.showinfo("Status", "No USB status records found for this user.")
        return

    status_color = "green" if latest_status == "Enabled" else "red"
    status_win = tk.Toplevel(root)
    status_win.title("USB Status Log")
    status_win.geometry("400x200")
    status_win.configure(bg="white")

    tk.Label(
        status_win,
        text="Current USB Status",
        font=("OCR A Extended", 14, "bold"),
        bg="white"
    ).pack(pady=20)

    tk.Label(
        status_win,
        text=f"USB Ports are {latest_status}",
        font=("OCR A Extended", 13),
        fg=status_color,
        bg="white"
    ).pack(pady=10)


root = tk.Tk()
root.title("USB Physical Security")
root.geometry("1000x620")

initialize_user_database()


def resource_path(relative_path):
    """Get the absolute path to an asset, works for dev and for PyInstaller bundle."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

background_image_path = resource_path("wallpaper.jpg")


try:
    background_image = Image.open(background_image_path)
    background_photo = ImageTk.PhotoImage(background_image)
    background_label = tk.Label(root, image=background_photo)
    background_label.place(relwidth=1, relheight=1)
except:
    root.configure(bg="white")

title_label = tk.Label(root, text="USB PHYSICAL SECURITY", font=("OCR A Extended", 19, "bold"), bg="#000000", fg="white")
title_label.pack(pady=20)

enable_button = tk.Button(root, text="Enable USB Ports", command=lambda: show_password_prompt(True), bg="#000000", fg="green", font=("OCR A Extended", 12, "bold"))
enable_button.place(relx=0.85, rely=0.90, anchor="center")

disable_button = tk.Button(root, text="Disable USB Ports", command=lambda: show_password_prompt(False), bg="#000000", fg="red", font=("OCR A Extended", 12, "bold"))
disable_button.place(relx=0.15, rely=0.90, anchor="center")

email_label = tk.Label(root, text="Send Secure Password via Email", font=("OCR A Extended", 14, "bold"), bg="#000000", fg="orange")
email_label.pack(pady=(30, 10))

email_entry = tk.Entry(root, font=("OCR A Extended", 12), width=40)
email_entry.pack(pady=5)
email_entry.insert(0, "Enter e-mail address")

send_button = tk.Button(root, text="Generate Password", command=send_password, bg="#000000", fg="gold", font=("OCR A Extended", 12, "bold"))
send_button.pack(pady=10)

view_users_button = tk.Button(root, text="View User Database", command=show_user_database, bg="#000000", fg="violet", font=("OCR A Extended", 12, "bold"))
view_users_button.pack(pady=10)

view_status_button = tk.Button(root, text="View Status", command=view_status_clicked, bg="#000000", fg="cyan", font=("OCR A Extended", 12, "bold"))
view_status_button.pack(pady=10)


def clear_placeholder(event):
    if email_entry.get() == "Enter e-mail address":
        email_entry.delete(0, tk.END)


def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


email_entry.bind("<FocusIn>", clear_placeholder)

for btn in [project_info_button, send_button, view_users_button, view_status_button, enable_button, disable_button]:
    btn.default_bg = btn['background']
    btn.bind("<Enter>", lambda e, b=btn: on_enter(e, b))
    btn.bind("<Leave>", lambda e, b=btn: on_leave(e, b))

success_label = tk.Label(root, text="", font=("Arial", 12), bg="#ffffff")
success_label.pack_forget()

root.mainloop()
