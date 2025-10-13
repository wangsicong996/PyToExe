import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import re
from mcrcon import MCRcon
import paramiko

# --------------------- Funkcje pomocnicze ---------------------

def remove_ansi_codes(text):
    return re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', text)

def ssh_tail_logs(ssh_host, ssh_port, ssh_user, ssh_pass, remote_log_path, console_widget, stop_event):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(ssh_host, port=ssh_port, username=ssh_user, password=ssh_pass, timeout=10)
    except Exception as e:
        messagebox.showerror("Błąd SSH", f"Nie udało się połączyć z serwerem:\n{e}")
        return False

    try:
        # 🔍 Sprawdź, czy plik loga istnieje
        stdin, stdout, stderr = client.exec_command(f'test -f "{remote_log_path}" && echo OK || echo MISSING')
        result = stdout.read().decode().strip()

        if result != "OK":
            messagebox.showerror("Błąd logów SSH", f"Nie znaleziono pliku loga:\n{remote_log_path}")
            client.close()
            return False

        cmd = f"tail -f {remote_log_path}"
        transport = client.get_transport()
        channel = transport.open_session()
        channel.exec_command(cmd)
        console_widget.insert_colored("[SSH] 📡 Tailowanie loga rozpoczęte.\n", "ssh")

        while not stop_event.is_set():
            if channel.recv_ready():
                data = channel.recv(4096).decode(errors="replace")
                for line in data.splitlines():
                    line_clean = remove_ansi_codes(line)
                    console_widget.insert_colored(f"[LOG] {line_clean}\n", "log")
            if channel.exit_status_ready():
                break
            time.sleep(0.1)

    except Exception as e:
        console_widget.insert_colored(f"[SSH] ⚠️ Błąd podczas tailowania: {e}\n", "error")

    finally:
        try:
            channel.close()
        except:
            pass
        client.close()
        # 🛑 Sprawdź czy konsola istnieje
        if console_widget.winfo_exists():
            console_widget.insert_colored("[SSH] 🔒 Połączenie zamknięte.\n", "ssh")
    return True


def rcon_loop(host, port, password, console_widget, stop_event):
    try:
        with MCRcon(host, password, port=port, timeout=10) as mcr:
            console_widget.insert_colored(f"[RCON] ✅ Połączono z {host}:{port}\n", "rcon")
            while not stop_event.is_set():
                cmd = console_widget.get_rcon_cmd()
                if cmd is None:
                    time.sleep(0.1)
                    continue
                if cmd.lower() in ("exit", "quit"):
                    console_widget.insert_colored("[RCON] Rozłączanie...\n", "rcon")
                    break
                try:
                    resp = mcr.command(cmd)
                    if not resp:
                        resp = "(brak odpowiedzi)"
                    console_widget.insert_colored(f"{resp}\n", "log")
                except Exception as e:
                    console_widget.insert_colored(f"[RCON BŁĄD] {e}\n", "error")
    except Exception as e:
        messagebox.showerror("Błąd RCON", f"Nie udało się połączyć z RCON:\n{e}")
        return False
    return True

# -------------------- Widget konsoli ------------------------

class ConsoleWidget(tk.Frame):
    """Konsola z kolorowym logiem i polem wpisywania"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.text = scrolledtext.ScrolledText(self, bg="black", fg="white", insertbackground="white",
                                              font=("Consolas", 10), state='disabled')
        self.text.pack(fill='both', expand=True, padx=5, pady=(5,0))

        # Tagowanie kolorów
        self.text.tag_config("rcon", foreground="#00aaff")   # niebieski
        self.text.tag_config("ssh", foreground="#00ff00")    # zielony
        self.text.tag_config("log", foreground="#cccccc")    # szary
        self.text.tag_config("error", foreground="#ff5555")  # czerwony

        entry_frame = tk.Frame(self)
        entry_frame.pack(fill='x', padx=5, pady=5)

        self.entry = ttk.Entry(entry_frame)
        self.entry.pack(side='left', fill='x', expand=True)
        self.entry.bind("<Return>", self.on_enter)

        send_btn = ttk.Button(entry_frame, text="Wyślij", command=self.on_send)
        send_btn.pack(side='right', padx=5)

        self.cmd_queue = []

    def insert_colored(self, text, tag=None):
        self.text.configure(state='normal')
        if tag:
            self.text.insert(tk.END, text, tag)
        else:
            self.text.insert(tk.END, text)
        self.text.configure(state='disabled')
        self.text.see(tk.END)

    def on_send(self):
        cmd = self.entry.get().strip()
        if cmd:
            self.cmd_queue.append(cmd)
            self.insert_colored(f"> {cmd}\n", "rcon")
            self.entry.delete(0, tk.END)

    def on_enter(self, event):
        self.on_send()
        return "break"

    def get_rcon_cmd(self):
        if self.cmd_queue:
            return self.cmd_queue.pop(0)
        return None

# -------------------- Główna aplikacja ------------------------

class RCONApp:
    def __init__(self, root):
        self.root = root
        root.title("🎮 RCON GUI")

        # ---- RCON ----
        ttk.Label(root, text="RCON host:").grid(row=0, column=0, sticky='e')
        self.rcon_host = ttk.Entry(root)
        self.rcon_host.grid(row=0, column=1)
        self.rcon_host.insert(0, "78.46.190.156")

        ttk.Label(root, text="RCON port:").grid(row=1, column=0, sticky='e')
        self.rcon_port = ttk.Entry(root)
        self.rcon_port.grid(row=1, column=1)
        self.rcon_port.insert(0, "25575")

        ttk.Label(root, text="RCON hasło:").grid(row=2, column=0, sticky='e')
        self.rcon_pass = ttk.Entry(root, show="*")
        self.rcon_pass.grid(row=2, column=1)

        # ---- SSH ----
        self.ssh_var = tk.BooleanVar(value=False)
        self.ssh_check = ttk.Checkbutton(root, text="Pokazuj logi (SSH)", variable=self.ssh_var, command=self.toggle_ssh_fields)
        self.ssh_check.grid(row=3, column=0, columnspan=2, sticky='w')

        ttk.Label(root, text="SSH host:").grid(row=4, column=0, sticky='e')
        self.ssh_host = ttk.Entry(root)
        self.ssh_host.grid(row=4, column=1)
        self.ssh_host.insert(0, "78.46.190.156")

        ttk.Label(root, text="SSH port:").grid(row=5, column=0, sticky='e')
        self.ssh_port = ttk.Entry(root)
        self.ssh_port.grid(row=5, column=1)
        self.ssh_port.insert(0, "22")

        ttk.Label(root, text="SSH user:").grid(row=6, column=0, sticky='e')
        self.ssh_user = ttk.Entry(root)
        self.ssh_user.grid(row=6, column=1)

        ttk.Label(root, text="SSH pass:").grid(row=7, column=0, sticky='e')
        self.ssh_pass = ttk.Entry(root, show="*")
        self.ssh_pass.grid(row=7, column=1)

        ttk.Label(root, text="Ścieżka do loga:").grid(row=8, column=0, sticky='e')
        self.ssh_log_path = ttk.Entry(root)
        self.ssh_log_path.grid(row=8, column=1)
        self.ssh_log_path.insert(0, "/home/gorcraft/logs/latest.log")

        # ---- Start ----
        self.start_btn = ttk.Button(root, text="Połącz", command=self.start_connection)
        self.start_btn.grid(row=9, column=0, columnspan=2, pady=5)

        self.toggle_ssh_fields()

        for child in root.winfo_children():
            child.grid_configure(padx=10, pady=5)

    def toggle_ssh_fields(self):
        state = 'normal' if self.ssh_var.get() else 'disabled'
        for widget in (self.ssh_host, self.ssh_port, self.ssh_user, self.ssh_pass, self.ssh_log_path):
            widget.config(state=state)

    def start_connection(self):
        host = self.rcon_host.get()
        port = int(self.rcon_port.get())
        password = self.rcon_pass.get()

        ssh_info = None
        if self.ssh_var.get():
            ssh_info = (
                self.ssh_host.get(),
                int(self.ssh_port.get()),
                self.ssh_user.get(),
                self.ssh_pass.get(),
                self.ssh_log_path.get()
            )

        # 🟡 Test połączenia SSH
        if ssh_info:
            test_client = paramiko.SSHClient()
            test_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                test_client.connect(ssh_info[0], port=ssh_info[1],
                                    username=ssh_info[2], password=ssh_info[3], timeout=10)
                stdin, stdout, _ = test_client.exec_command(f'test -f "{ssh_info[4]}" && echo OK || echo MISSING')
                result = stdout.read().decode().strip()
                if result != "OK":
                    messagebox.showerror("Błąd logów SSH", f"Nie znaleziono pliku loga:\n{ssh_info[4]}")
                    test_client.close()
                    return
            except Exception as e:
                messagebox.showerror("Błąd SSH", f"Nie udało się połączyć z serwerem SSH:\n{e}")
                return
            finally:
                test_client.close()

        self.root.withdraw()
        self.open_console(host, port, password, ssh_info)

    def open_console(self, host, port, password, ssh_info):
        console_win = tk.Toplevel()
        console_win.title("🖥️ Konsola RCON")
        console = ConsoleWidget(console_win)
        console.pack(fill='both', expand=True)

        stop_event = threading.Event()

        def disconnect():
            stop_event.set()
            console.insert_colored("\n[RCON] Rozłączanie...\n", "rcon")
            console_win.destroy()
            self.root.deiconify()

        btn_disconnect = ttk.Button(console_win, text="🔌 Rozłącz", command=disconnect)
        btn_disconnect.pack(pady=5)

        threading.Thread(target=rcon_loop, args=(host, port, password, console, stop_event), daemon=True).start()

        if ssh_info:
            threading.Thread(target=ssh_tail_logs, args=(*ssh_info, console, stop_event), daemon=True).start()


# -------------------- Uruchomienie ------------------------

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(False, False)
    app = RCONApp(root)
    root.mainloop()
