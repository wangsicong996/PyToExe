#!/usr/bin/env python3
"""
File Encryptor GUI (AES-GCM, PBKDF2 with 500000 iterations)

Usage: Run with Python 3.10+ and required packages from requirements.txt.
Build into an .exe on Windows with PyInstaller (instructions in README.txt).
"""

import os
import sys
import threading
import traceback
from pathlib import Path
from tkinter import Tk, StringVar, filedialog, messagebox, ttk, LEFT, RIGHT, BOTH, X, Y, END
import tkinter as tk

# Cryptography imports
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import secrets
import base64

# Constants
HEADER = b'ENCRYPTEDv1'  # 10 bytes
SALT_SIZE = 16
NONCE_SIZE = 12
KEY_LEN = 32
ITERATIONS = 500000  # per user request

def derive_key(password: str, salt: bytes) -> bytes:
    password_bytes = password.encode('utf-8')
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LEN,
        salt=salt,
        iterations=ITERATIONS,
    )
    key = kdf.derive(password_bytes)
    return key

def encrypt_bytes(data: bytes, password: str) -> bytes:
    salt = secrets.token_bytes(SALT_SIZE)
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    nonce = secrets.token_bytes(NONCE_SIZE)
    ct = aesgcm.encrypt(nonce, data, None)
    # Format: HEADER | salt | nonce | ciphertext
    return HEADER + salt + nonce + ct

def decrypt_bytes(blob: bytes, password: str) -> bytes:
    if not blob.startswith(HEADER):
        raise ValueError("File does not have expected header (not an encrypted file by this program).")
    offset = len(HEADER)
    salt = blob[offset:offset+SALT_SIZE]; offset += SALT_SIZE
    nonce = blob[offset:offset+NONCE_SIZE]; offset += NONCE_SIZE
    ct = blob[offset:]
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    pt = aesgcm.decrypt(nonce, ct, None)
    return pt

def encrypt_file(path: Path, password: str, out_path: Path=None) -> None:
    if out_path is None:
        out_path = path.with_suffix(path.suffix + '.enc')
    with open(path, 'rb') as f:
        data = f.read()
    enc = encrypt_bytes(data, password)
    with open(out_path, 'wb') as f:
        f.write(enc)

def decrypt_file(path: Path, password: str, out_path: Path=None) -> None:
    if out_path is None:
        # remove .enc if present
        name = path.name
        if name.endswith('.enc'):
            out_name = name[:-4]
        else:
            out_name = name + '.dec'
        out_path = path.with_name(out_name)
    with open(path, 'rb') as f:
        blob = f.read()
    pt = decrypt_bytes(blob, password)
    with open(out_path, 'wb') as f:
        f.write(pt)

def process_paths(paths, password, mode, progress_callback=None):
    # mode: 'encrypt' or 'decrypt'
    all_files = []
    for p in paths:
        p = Path(p)
        if p.is_dir():
            for root, dirs, files in os.walk(p):
                for fn in files:
                    all_files.append(Path(root) / fn)
        else:
            all_files.append(p)
    total = len(all_files)
    for idx, filep in enumerate(all_files, start=1):
        try:
            if mode == 'encrypt':
                encrypt_file(filep, password)
            else:
                decrypt_file(filep, password)
            status = f"{mode.title()}ed: {filep}"
        except Exception as e:
            status = f"Error on {filep}: {e}"
        if progress_callback:
            progress_callback(idx, total, status)
    return

# --- GUI ---
class App:
    def __init__(self, root):
        self.root = root
        root.title("Encryptor — Simple & Clean")
        root.geometry("680x380")
        root.resizable(False, False)
        # Root style
        style = ttk.Style(root)
        style.theme_use('clam')
        style.configure('TButton', padding=6, relief='flat', font=('Segoe UI', 10))
        style.configure('TLabel', font=('Segoe UI', 10))
        style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'))

        frm = ttk.Frame(root, padding=16)
        frm.pack(fill=BOTH, expand=True)

        ttk.Label(frm, text="Encryptor", style='Header.TLabel').pack(anchor='w')
        ttk.Label(frm, text="Sélectionnez des fichiers ou dossiers, entrez une clé, puis choisissez chiffrer ou déchiffrer.").pack(anchor='w', pady=(0,10))

        # File selection list
        self.paths_var = StringVar(value="Aucun fichier sélectionné")
        self.paths_display = tk.Text(frm, height=6, wrap='word')
        self.paths_display.insert('1.0', "Aucun fichier sélectionné")
        self.paths_display.configure(state='disabled', bg=root.cget('bg'), bd=0, relief='flat')
        self.paths_display.pack(fill=X, pady=(0,8))

        btn_row = ttk.Frame(frm)
        btn_row.pack(fill=X)
        ttk.Button(btn_row, text="Ajouter fichiers", command=self.add_files).pack(side=LEFT, padx=(0,8))
        ttk.Button(btn_row, text="Ajouter dossier", command=self.add_folder).pack(side=LEFT, padx=(0,8))
        ttk.Button(btn_row, text="Effacer la sélection", command=self.clear_selection).pack(side=LEFT)

        # Password entry
        pw_row = ttk.Frame(frm)
        pw_row.pack(fill=X, pady=(12,0))
        ttk.Label(pw_row, text="Clé privée (mot de passe) :").pack(anchor='w')
        self.pw_entry = ttk.Entry(pw_row, show='*', width=60)
        self.pw_entry.pack(anchor='w', pady=(4,0))

        # Action buttons
        action_row = ttk.Frame(frm)
        action_row.pack(fill=X, pady=(12,0))
        ttk.Button(action_row, text="Chiffrer", command=lambda: self.start('encrypt')).pack(side=LEFT, padx=(0,8))
        ttk.Button(action_row, text="Déchiffrer", command=lambda: self.start('decrypt')).pack(side=LEFT, padx=(0,8))
        ttk.Button(action_row, text="Quitter", command=root.quit).pack(side=RIGHT)

        # Progress & status
        self.progress = ttk.Progressbar(frm, mode='determinate')
        self.progress.pack(fill=X, pady=(16,4))
        self.status_var = StringVar(value="Prêt")
        ttk.Label(frm, textvariable=self.status_var).pack(anchor='w')

        self.selected = []

    def add_files(self):
        files = filedialog.askopenfilenames(title="Sélectionner des fichiers")
        if files:
            self.selected.extend(list(files))
            self.refresh_list()

    def add_folder(self):
        folder = filedialog.askdirectory(title="Sélectionner un dossier")
        if folder:
            self.selected.append(folder)
            self.refresh_list()

    def clear_selection(self):
        self.selected = []
        self.refresh_list()

    def refresh_list(self):
        self.paths_display.configure(state='normal')
        self.paths_display.delete('1.0', END)
        if not self.selected:
            self.paths_display.insert('1.0', "Aucun fichier sélectionné")
        else:
            for p in self.selected:
                self.paths_display.insert(END, str(p) + "\\n")
        self.paths_display.configure(state='disabled')

    def start(self, mode):
        pw = self.pw_entry.get().strip()
        if not self.selected:
            messagebox.showwarning("Aucun fichier", "Aucune sélection. Ajoutez un fichier ou un dossier.")
            return
        if not pw:
            messagebox.showwarning("Clé manquante", "Entrez une clé privée (mot de passe).")
            return
        # disable UI
        self.status_var.set(f"{mode.title()} en cours...")
        self.progress['value'] = 0
        self.root.update_idletasks()
        thread = threading.Thread(target=self.run_process, args=(list(self.selected), pw, mode), daemon=True)
        thread.start()

    def run_process(self, paths, pw, mode):
        def progress_cb(idx, total, status):
            pct = int((idx/total)*100) if total>0 else 0
            self.progress['value'] = pct
            self.status_var.set(status)
            self.root.update_idletasks()
        try:
            process_paths(paths, pw, mode, progress_cb)
            messagebox.showinfo("Terminé", f"{mode.title()} terminé.")
            self.status_var.set("Prêt")
            self.progress['value'] = 0
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Erreur", f"Une erreur est survenue:\\n{e}")
            self.status_var.set("Erreur")

def main():
    root = Tk()
    app = App(root)
    root.mainloop()

if __name__ == '__main__':
    main()
