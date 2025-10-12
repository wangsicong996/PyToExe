import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, ttk
import os
import json
from PIL import Image, ImageTk
import ctypes
import tempfile
import subprocess

SAVE_FILE = "games.json"

# Charger ou initialiser la liste
if os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, "r") as f:
        games = json.load(f)
else:
    games = []

# Extraire l'icône d'un exe (Windows)
def get_icon(exe_path):
    ico_x = ico_y = 32
    hicon = ctypes.windll.shell32.ExtractIconW(0, exe_path, 0)
    if hicon == 0:
        return None
    hdc = ctypes.windll.user32.GetDC(0)
    hdcMem = ctypes.windll.gdi32.CreateCompatibleDC(hdc)
    hbm = ctypes.windll.gdi32.CreateCompatibleBitmap(hdc, ico_x, ico_y)
    ctypes.windll.gdi32.SelectObject(hdcMem, hbm)
    ctypes.windll.user32.DrawIconEx(hdcMem, 0, 0, hicon, ico_x, ico_y, 0, 0, 3)
    temp_file = os.path.join(tempfile.gettempdir(), os.path.basename(exe_path) + ".png")
    # Convertir le HBITMAP en image avec PIL
    # Alternative simple : utiliser une icône par défaut si compliqué
    return temp_file

# Sauvegarder les jeux
def save_games():
    with open(SAVE_FILE, "w") as f:
        json.dump(games, f, indent=4)

# Ajouter un jeu
def add_game():
    exe_path = filedialog.askopenfilename(filetypes=[("Executable files", "*.exe")])
    if exe_path:
        name = simpledialog.askstring("Nom du jeu", "Entrez le nom du jeu :", initialvalue=os.path.basename(exe_path))
        games.append({"name": name, "path": exe_path})
        save_games()
        update_treeview()

# Renommer un jeu
def rename_game():
    selected = tree.selection()
    if not selected:
        return
    index = int(selected[0])
    new_name = simpledialog.askstring("Renommer", "Entrez le nouveau nom :", initialvalue=games[index]["name"])
    if new_name:
        games[index]["name"] = new_name
        save_games()
        update_treeview()

# Supprimer un jeu
def remove_game():
    selected = tree.selection()
    if not selected:
        return
    index = int(selected[0])
    del games[index]
    save_games()
    update_treeview()

# Lancer un jeu
def launch_game(event=None):
    selected = tree.selection()
    if not selected:
        return
    index = int(selected[0])
    exe_path = games[index]["path"]
    if os.path.exists(exe_path):
        subprocess.Popen(exe_path)
    else:
        messagebox.showerror("Erreur", "Le fichier n'existe plus.")

# Mettre à jour l'affichage
def update_treeview():
    for i in tree.get_children():
        tree.delete(i)
    for i, game in enumerate(games):
        tree.insert("", "end", iid=i, values=(game["name"], game["path"]))

root = tk.Tk()
root.title("Gestionnaire de jeux")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10, fill="both", expand=True)

tree = ttk.Treeview(frame, columns=("Nom", "Chemin"), show="headings")
tree.heading("Nom", text="Nom")
tree.heading("Chemin", text="Chemin")
tree.pack(fill="both", expand=True)
tree.bind("<Double-1>", launch_game)

btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)

tk.Button(btn_frame, text="Ajouter", command=add_game).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Renommer", command=rename_game).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="Supprimer", command=remove_game).grid(row=0, column=2, padx=5)

update_treeview()
root.mainloop()
