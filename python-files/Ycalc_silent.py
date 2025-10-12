# Ycalc_silent.py
# 直噴Y計算器（靜音版，不顯示黑視窗）
import sys, os, tkinter as tk
from tkinter import messagebox

# 若使用者意外用 python.exe 開啟，則自動重啟為 pythonw.exe
if sys.executable.lower().endswith("python.exe"):
    pythonw = sys.executable.replace("python.exe", "pythonw.exe")
    os.startfile(pythonw + " " + os.path.abspath(__file__))
    sys.exit()

def calculate():
    try:
        x = float(entry_x.get())
        y = (430 - x) / 2
        label_result.config(text=f"Y = {y:.2f}")
    except ValueError:
        messagebox.showerror("錯誤", "請輸入有效的數字（可含小數）！")

root = tk.Tk()
root.title("直噴Y計算器")
root.geometry("280x160")
root.resizable(False, False)
root.configure(bg="#eef3fc")

title_label = tk.Label(root, text="直噴Y計算器", font=("Segoe UI", 14, "bold"), bg="#eef3fc", fg="#1a73e8")
title_label.pack(pady=10)

frame = tk.Frame(root, bg="#eef3fc")
frame.pack()

tk.Label(frame, text="輸入 X 值（可含小數）:", bg="#eef3fc", font=("Segoe UI", 10)).grid(row=0, column=0, padx=5, pady=5)
entry_x = tk.Entry(frame, width=12, font=("Segoe UI", 10))
entry_x.grid(row=0, column=1, padx=5, pady=5)

tk.Button(root, text="計算", command=calculate, bg="#1a73e8", fg="white", font=("Segoe UI", 10), width=10).pack(pady=10)
label_result = tk.Label(root, text="Y = ", font=("Segoe UI", 12), bg="#eef3fc")
label_result.pack()

root.mainloop()
