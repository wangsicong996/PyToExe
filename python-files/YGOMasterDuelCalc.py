#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Yu-Gi-Oh! Local Calculator (Tkinter)
Features:
 - Two players with names and Life Points (LP)
 - Quick +/- buttons and custom amount input
 - Add free-text events to temporary history
 - History list with timestamps (in-memory only)
 - Undo last action (restores previous LPs)
 - Coin flip & dice roll
 - Turn counter
 - Reset / New match
 - Greek UI
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
from datetime import datetime

# ---------- Config ----------
DEFAULT_LP = 8000

# ---------- App ----------
class YugiohCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Yu-Gi-Oh! Calculator")
        self.geometry("900x600")
        self.minsize(800, 520)

        # State
        self.p1_name = tk.StringVar(value="Παίκτης 1")
        self.p2_name = tk.StringVar(value="Παίκτης 2")
        self.p1_lp = tk.IntVar(value=DEFAULT_LP)
        self.p2_lp = tk.IntVar(value=DEFAULT_LP)
        self.turn = tk.IntVar(value=1)
        self.history = []  # list of dicts: {time, desc, p1_lp, p2_lp}
        self.undo_stack = []  # stack of previous LP pairs for undo

        # Build UI
        self.create_widgets()

    def create_widgets(self):
        # Top: Player frames
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", padx=10, pady=8)

        self.player_frame(top_frame, 0, self.p1_name, self.p1_lp, self.adjust_p1)
        self.player_frame(top_frame, 1, self.p2_name, self.p2_lp, self.adjust_p2)

        # Middle controls: custom input, coin/dice, turn controls
        mid_frame = ttk.Frame(self)
        mid_frame.pack(fill="x", padx=10, pady=6)

        # Custom amount and quick buttons
        amount_frame = ttk.LabelFrame(mid_frame, text="Ενέργεια LP / Εισαγωγή")
        amount_frame.grid(row=0, column=0, sticky="nsew", padx=6, pady=4)

        self.custom_amount = tk.StringVar(value="500")
        ttk.Label(amount_frame, text="Ποσό (θετικό/αρνητικό):").grid(row=0, column=0, sticky="w")
        ttk.Entry(amount_frame, textvariable=self.custom_amount, width=12).grid(row=0, column=1, sticky="w")

        # Quick buttons
        quicks = [100, 500, 1000, 2000]
        qb_frame = ttk.Frame(amount_frame)
        qb_frame.grid(row=1, column=0, columnspan=2, pady=4)
        for q in quicks:
            ttk.Button(qb_frame, text=f"±{q}", command=lambda v=q: self.set_custom_sign_buttons(v)).pack(side="left", padx=4)

        ttk.Button(amount_frame, text="Εφαρμογή σε Παίκτη 1", command=lambda: self.apply_amount('p1')).grid(row=2, column=0, pady=6)
        ttk.Button(amount_frame, text="Εφαρμογή σε Παίκτη 2", command=lambda: self.apply_amount('p2')).grid(row=2, column=1, pady=6)

        # Notes & add to history
        note_frame = ttk.LabelFrame(mid_frame, text="Σημείωση / Προσθήκη στο Ιστορικό")
        note_frame.grid(row=0, column=1, sticky="nsew", padx=6, pady=4)
        self.note_text = tk.StringVar()
        ttk.Entry(note_frame, textvariable=self.note_text, width=40).grid(row=0, column=0, padx=6, pady=6)
        ttk.Button(note_frame, text="Προσθήκη", command=self.add_note_to_history).grid(row=0, column=1, padx=6)

        # Coin flip & dice
        tools_frame = ttk.LabelFrame(mid_frame, text="Τυχαία")
        tools_frame.grid(row=0, column=2, sticky="nsew", padx=6, pady=4)
        ttk.Button(tools_frame, text="Coin Flip", command=self.coin_flip).grid(row=0, column=0, padx=6, pady=4)
        ttk.Button(tools_frame, text="Ζάρι (1-6)", command=self.dice_roll).grid(row=0, column=1, padx=6, pady=4)

        # Turn counter & actions
        turn_frame = ttk.LabelFrame(mid_frame, text="Γύρος / Διαχείριση")
        turn_frame.grid(row=0, column=3, sticky="nsew", padx=6, pady=4)
        ttk.Label(turn_frame, text="Γύρος:").grid(row=0, column=0)
        self.turn_label = ttk.Label(turn_frame, textvariable=self.turn, width=6)
        self.turn_label.grid(row=0, column=1)
        ttk.Button(turn_frame, text="Επόμενος Γύρος", command=self.next_turn).grid(row=1, column=0, columnspan=2, pady=4)
        ttk.Button(turn_frame, text="Undo", command=self.undo).grid(row=2, column=0, columnspan=2, pady=4)
        ttk.Button(turn_frame, text="Reset Match", command=self.reset_match).grid(row=3, column=0, columnspan=2, pady=4)

        # Bottom: History and log
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill="both", expand=True, padx=10, pady=6)

        history_frame = ttk.LabelFrame(bottom_frame, text="Ιστορικό (προσωρινό)")
        history_frame.pack(fill="both", expand=True, side="left", padx=6, pady=4)

        self.history_list = tk.Listbox(history_frame)
        self.history_list.pack(fill="both", expand=True, padx=6, pady=6)
        bl_frame = ttk.Frame(history_frame)
        bl_frame.pack(fill="x", padx=6, pady=4)
        ttk.Button(bl_frame, text="Εξαγωγή σε αρχείο (προαιρετικό)", command=self.export_history).pack(side="left")
        ttk.Button(bl_frame, text="Διαγραφή επιλεγμένου", command=self.delete_selected_history).pack(side="left", padx=6)

        # Footer: instructions
        footer = ttk.Label(bottom_frame, text="Σημείωση: Το ιστορικό είναι προσωρινό — αποθηκεύεται μόνο στην τρέχουσα συνεδρία.", foreground="gray")
        footer.pack(fill="x", padx=6, pady=4, side="bottom")

    def player_frame(self, parent, col, name_var, lp_var, adjust_callback):
        frame = ttk.LabelFrame(parent, text=f"Παίκτης {col+1}")
        frame.grid(row=0, column=col, padx=10, pady=4, sticky="nsew")
        parent.columnconfigure(col, weight=1)

        # Name
        name_entry = ttk.Entry(frame, textvariable=name_var, width=20)
        name_entry.grid(row=0, column=0, padx=6, pady=6)

        # LP display
        lp_label = ttk.Label(frame, textvariable=lp_var, font=("Helvetica", 28))
        lp_label.grid(row=1, column=0, padx=6, pady=6)

        # +/- buttons for common operations for this player
        btns = ttk.Frame(frame)
        btns.grid(row=2, column=0, pady=6)
        ttk.Button(btns, text="-500", command=lambda: adjust_callback(-500)).pack(side="left", padx=4)
        ttk.Button(btns, text="-1000", command=lambda: adjust_callback(-1000)).pack(side="left", padx=4)
        ttk.Button(btns, text="+500", command=lambda: adjust_callback(500)).pack(side="left", padx=4)
        ttk.Button(btns, text="+1000", command=lambda: adjust_callback(1000)).pack(side="left", padx=4)

        # custom apply & set name
        ttk.Button(frame, text="Set Όνομα (παραθύρου)", command=lambda: self.set_name_dialog(name_var)).grid(row=3, column=0, pady=6)

    def set_name_dialog(self, var):
        new = simpledialog.askstring("Ορισμός ονόματος", "Γράψε όνομα:", initialvalue=var.get(), parent=self)
        if new:
            var.set(new)

    def set_custom_sign_buttons(self, v):
        # toggles sign example: set custom_amount to positive/negative depending on current sign
        try:
            amt = int(self.custom_amount.get())
        except Exception:
            amt = v
        # if current negative, make positive, else negative — but keep magnitude v
        if amt < 0:
            self.custom_amount.set(str(abs(v)))
        else:
            self.custom_amount.set(str(-abs(v)))

    def apply_amount(self, player_key):
        # parse custom amount
        try:
            amt = int(self.custom_amount.get())
        except Exception:
            messagebox.showerror("Σφάλμα", "Μη έγκυρο ποσό. Βάλε ακέραιο αριθμό (π.χ. 500 ή -300).")
            return
        self.record_undo()  # save before change
        if player_key == 'p1':
            self.p1_lp.set(max(0, self.p1_lp.get() + amt))
        else:
            self.p2_lp.set(max(0, self.p2_lp.get() + amt))
        # add to history
        pname = self.p1_name.get() if player_key == 'p1' else self.p2_name.get()
        desc = f"{pname} {'+' if amt>0 else ''}{amt}"
        self.push_history(desc)

    def adjust_p1(self, delta):
        self.record_undo()
        self.p1_lp.set(max(0, self.p1_lp.get() + delta))
        self.push_history(f"{self.p1_name.get()} {delta:+d}")

    def adjust_p2(self, delta):
        self.record_undo()
        self.p2_lp.set(max(0, self.p2_lp.get() + delta))
        self.push_history(f"{self.p2_name.get()} {delta:+d}")

    def record_undo(self):
        # push current LPs onto undo stack
        self.undo_stack.append((self.p1_lp.get(), self.p2_lp.get()))
        # limit undo depth to something reasonable
        if len(self.undo_stack) > 100:
            self.undo_stack.pop(0)

    def push_history(self, desc):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {desc} | {self.p1_name.get()}: {self.p1_lp.get()}  —  {self.p2_name.get()}: {self.p2_lp.get()}"
        self.history.append(entry)
        self.history_list.insert("end", entry)
        # auto-scroll
        self.history_list.yview_moveto(1)

    def add_note_to_history(self):
        note = self.note_text.get().strip()
        if not note:
            messagebox.showinfo("Πληροφορία", "Γράψε κάτι πριν πατήσεις Προσθήκη.")
            return
        self.push_history(f"Σημείωση: {note}")
        self.note_text.set("")

    def coin_flip(self):
        res = random.choice(["Κορώνα", "Γράμματα"])
        self.push_history(f"Coin flip → {res}")
        messagebox.showinfo("Coin Flip", f"Αποτέλεσμα: {res}")

    def dice_roll(self):
        res = random.randint(1,6)
        self.push_history(f"Ζάρι → {res}")
        messagebox.showinfo("Ζάρι", f"Έπεσε: {res}")

    def next_turn(self):
        self.turn.set(self.turn.get() + 1)
        self.push_history(f"Next Turn → {self.turn.get()}")

    def undo(self):
        if not self.undo_stack:
            messagebox.showinfo("Undo", "Δεν υπάρχουν ενέργειες για αναίρεση.")
            return
        prev_p1, prev_p2 = self.undo_stack.pop()
        self.p1_lp.set(prev_p1)
        self.p2_lp.set(prev_p2)
        self.push_history("Undo (αναίρεση τελευταίας ενέργειας)")

    def reset_match(self):
        if not messagebox.askyesno("Reset", "Θες να ξεκινήσεις νέα παρτίδα; Το ιστορικό θα παραμείνει.") :
            return
        # record undo and reset LPs and turn
        self.record_undo()
        self.p1_lp.set(DEFAULT_LP)
        self.p2_lp.set(DEFAULT_LP)
        self.turn.set(1)
        self.push_history("Reset match (νέα παρτίδα)")

    def export_history(self):
        # simple export to a text file (optional). It's okay — user asked for temporary history, but provide exporting choice.
        try:
            fname = simpledialog.askstring("Εξαγωγή", "Όνομα αρχείου (π.χ. history.txt):", initialvalue="yugioh_history.txt", parent=self)
            if not fname:
                return
            with open(fname, "w", encoding="utf-8") as f:
                for line in self.history:
                    f.write(line + "\n")
            messagebox.showinfo("Επιτυχία", f"Ιστορικό εξήχθη στο αρχείο: {fname}")
        except Exception as e:
            messagebox.showerror("Σφάλμα", f"Σφάλμα εξαγωγής: {e}")

    def delete_selected_history(self):
        sel = self.history_list.curselection()
        if not sel:
            messagebox.showinfo("Διαγραφή", "Επίλεξε πρώτα μία καταγραφή από το ιστορικό.")
            return
        idx = sel[0]
        self.history_list.delete(idx)
        try:
            del self.history[idx]
        except Exception:
            pass

# Run app
if __name__ == "__main__":
    app = YugiohCalculator()
    app.mainloop()
