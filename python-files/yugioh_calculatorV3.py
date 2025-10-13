import tkinter as tk
import random, time, threading

# ---------------- Colors & Fonts ----------------
bg_color = "#0f1115"
panel_bg_color = "#111318"
panel_outline_color = "#00e5ff"
name_fg_color = "#bffcff"
lp_fg_color = "#00ffcc"
btn_bg_color = "#222427"
btn_plus_color = "#00ff88"
btn_minus_color = "#ff6677"
half_bg_color = "#2a2a2a"
half_fg_color = "#ffd24d"
btn_hover_color = "#444444"
glow_heal_color = "#19ffb8"
glow_damage_color = "#ff4c4c"
glow_half_color = "#ffd24d"

fonts = {
    "name": ("Arial", 24, "bold"),
    "lp": ("Arial", 48, "bold"),
    "btn": ("Arial", 16, "bold")
}

# ---------------- App State ----------------
players = []
history = []
undo_stack = []

# ---------------- UI Helpers ----------------
def animate_number(var, start, end, bar_canvas=None, bar_rect=None, glow_color=None):
    steps = 20
    diff = end - start
    def step(i=1):
        val = int(start + diff * (i/steps))
        var.set(val)
        if bar_canvas and bar_rect:
            bar_width = int((val/8000)*bar_canvas.winfo_width())
            bar_canvas.coords(bar_rect, 0,0,bar_width,20)
            bar_canvas.itemconfig(bar_rect, fill=glow_color)
        if i<steps:
            root.after(20, lambda: step(i+1))
        else:
            var.set(end)
            if bar_canvas and bar_rect:
                bar_canvas.itemconfig(bar_rect, fill="#00ffcc")
    step()

def add_hover(widget):
    def on_enter(e):
        widget['bg'] = btn_hover_color
    def on_leave(e):
        widget['bg'] = btn_bg_color
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

# ---------------- Player Panels ----------------
def add_player():
    if len(players)>=4:
        return
    idx = len(players)
    players.append({"name":f"Player {idx+1}","lp":8000})
    create_player_panel(idx)

def create_player_panel(idx):
    panel=tk.Frame(players_frame,bg=panel_bg_color,bd=5,relief="ridge")
    panel.grid(row=idx//2,column=idx%2,padx=20,pady=20,sticky="nsew")
    players_frame.grid_rowconfigure(idx//2,weight=1)
    players_frame.grid_columnconfigure(idx%2,weight=1)

    name_var=tk.StringVar(value=players[idx]["name"])
    name_entry=tk.Entry(panel,textvariable=name_var,font=fonts["name"],fg=name_fg_color,bg=panel_bg_color,justify="center",bd=0)
    name_entry.pack(pady=(10,8))
    players[idx]["name_var"]=name_var

    # LP display
    lp_var = tk.IntVar(value=8000)
    lbl = tk.Label(panel,textvariable=lp_var,font=fonts["lp"],fg=lp_fg_color,bg=panel_bg_color)
    lbl.pack(pady=8)
    players[idx]["lp_var"]=lp_var
    players[idx]["lbl"]=lbl

    # LP bar
    bar_canvas=tk.Canvas(panel,width=360,height=20,bg="#222427",highlightthickness=0)
    bar_canvas.pack(pady=(0,10))
    bar_rect=bar_canvas.create_rectangle(0,0,360,20,fill="#00ffcc")
    players[idx]["bar_canvas"]=bar_canvas
    players[idx]["bar_rect"]=bar_rect

    # Buttons
    btns=tk.Frame(panel,bg=panel_bg_color)
    btns.pack()
    plus_row=tk.Frame(btns,bg=panel_bg_color)
    plus_row.pack()
    minus_row=tk.Frame(btns,bg=panel_bg_color)
    minus_row.pack(pady=(5,0))
    for amt in [50,100,500,1000]:
        b=tk.Button(plus_row,text=f"+{amt}",command=lambda a=amt,i=idx: change_lp(i,a),bg=btn_bg_color,fg=btn_plus_color,font=fonts["btn"],width=7)
        b.pack(side="left",padx=5); add_hover(b)
    for amt in [50,100,500,1000]:
        b2=tk.Button(minus_row,text=f"-{amt}",command=lambda a=amt,i=idx: change_lp(i,-a),bg=btn_bg_color,fg=btn_minus_color,font=fonts["btn"],width=7)
        b2.pack(side="left",padx=5); add_hover(b2)
    half_btn = tk.Button(btns,text="Half LP",command=lambda i=idx: half_lp(i),bg=half_bg_color,fg=half_fg_color,font=fonts["btn"],width=16)
    half_btn.pack(pady=5); add_hover(half_btn)

# ---------------- LP / History Functions ----------------
def change_lp(idx, amount):
    undo_stack.append((idx, players[idx]["lp"]))
    old = players[idx]["lp"]
    new = max(0, old + amount)
    players[idx]["lp"]=new
    animate_number(players[idx]["lp_var"], old, new, bar_canvas=players[idx]["bar_canvas"], bar_rect=players[idx]["bar_rect"], glow_color=glow_heal_color if amount>0 else glow_damage_color)
    history.insert(0,f"{time.strftime('%H:%M:%S')} - {players[idx]['name_var'].get()} {'+' if amount>0 else ''}{amount} LP")
    update_history_ui()

def half_lp(idx):
    undo_stack.append((idx, players[idx]["lp"]))
    old = players[idx]["lp"]
    new = old//2
    players[idx]["lp"]=new
    animate_number(players[idx]["lp_var"], old, new, bar_canvas=players[idx]["bar_canvas"], bar_rect=players[idx]["bar_rect"], glow_color=glow_half_color)
    history.insert(0,f"{time.strftime('%H:%M:%S')} - {players[idx]['name_var'].get()} Half LP")
    update_history_ui()

def reset_all():
    for i,p in enumerate(players):
        players[i]["lp"]=8000
        players[i]["lp_var"].set(8000)
        players[i]["bar_canvas"].coords(players[i]["bar_rect"],0,0,360,20)
    history.insert(0,f"{time.strftime('%H:%M:%S')} - New Game")
    undo_stack.clear()
    update_history_ui()

def undo_action():
    if not undo_stack: return
    idx,old=undo_stack.pop()
    players[idx]["lp"]=old
    players[idx]["lp_var"].set(old)
    bar_canvas = players[idx]["bar_canvas"]
    players[idx]["bar_canvas"].coords(players[idx]["bar_rect"],0,0,int((old/8000)*360),20)
    history.insert(0,f"{time.strftime('%H:%M:%S')} - Undo for {players[idx]['name_var'].get()}")
    update_history_ui()

def update_history_ui():
    history_box.config(state="normal")
    history_box.delete("1.0","end")
    history_box.insert("1.0","\n".join(history[:250]))
    history_box.config(state="disabled")

# ---------------- Dice / Coin ----------------
def roll_dice():
    for _ in range(12):
        v=random.randint(1,6)
        dice_label.config(text=f"Dice: {v}")
        root.update(); time.sleep(0.04)
    history.insert(0,f"{time.strftime('%H:%M:%S')} - Dice rolled: {v}")
    update_history_ui()

def flip_coin():
    for _ in range(12):
        r=random.choice(["Heads","Tails"])
        coin_label.config(text=f"Coin: {r}")
        root.update(); time.sleep(0.04)
    history.insert(0,f"{time.strftime('%H:%M:%S')} - Coin: {r}")
    update_history_ui()

# ---------------- Build UI ----------------
root=tk.Tk()
root.title("Yu-Gi-Oh! LP Calculator v4.2")
root.configure(bg=bg_color)
root.state("zoomed")
root.geometry("1920x1080")

top_frame=tk.Frame(root,bg=bg_color)
top_frame.pack(pady=10)
btn_specs=[("Add Player",add_player),("Reset All",reset_all),("Undo",undo_action),("Roll Dice",roll_dice),("Flip Coin",flip_coin)]
for t,c in btn_specs:
    b=tk.Button(top_frame,text=t,command=c,bg=btn_bg_color,fg=lp_fg_color,width=16,font=fonts["btn"])
    b.pack(side="left",padx=8); add_hover(b)

players_frame=tk.Frame(root,bg=bg_color)
players_frame.pack(fill="both",expand=True,padx=12,pady=12)
players_frame.columnconfigure(0,weight=1)
players_frame.columnconfigure(1,weight=1)

dice_label=tk.Label(root,text="Dice: -",fg=lp_fg_color,bg=bg_color,font=fonts["btn"])
dice_label.pack(pady=4)
coin_label=tk.Label(root,text="Coin: -",fg=lp_fg_color,bg=bg_color,font=fonts["btn"])
coin_label.pack(pady=4)

history_box=tk.Text(root,height=8,state="disabled",bg=bg_color,fg=lp_fg_color,font=fonts["btn"])
history_box.pack(fill="both",padx=12,pady=8)

# Δημιουργία δύο αρχικών παικτών
for _ in range(2): add_player()

root.mainloop()
