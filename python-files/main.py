import customtkinter as ctk
from tkinter import messagebox
import threading
import time
from pynput import mouse, keyboard
import win32api
import win32con
import ctypes
import json
import os

class FFSensiApp:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("FF SENSI - Pro Sensitivity Tool")
        self.window.geometry("600x750")
        self.window.resizable(False, False)
        
        # Variables
        self.is_active = False
        self.aim_shake_fix = ctk.BooleanVar(value=False)
        self.aim_smooth = ctk.BooleanVar(value=False)
        self.recoil_reduce = ctk.BooleanVar(value=False)
        self.smooth_drag = ctk.BooleanVar(value=False)
        
        # Sensitivity values
        self.aim_shake_value = ctk.DoubleVar(value=50)
        self.aim_smooth_value = ctk.DoubleVar(value=50)
        self.recoil_value = ctk.DoubleVar(value=50)
        self.drag_smooth_value = ctk.DoubleVar(value=50)
        
        # Theme colors
        self.themes = {
            "Purple": ("#8B5CF6", "#6D28D9"),
            "Blue": ("#3B82F6", "#1E40AF"),
            "Red": ("#EF4444", "#B91C1C"),
            "Green": ("#10B981", "#047857"),
            "Orange": ("#F97316", "#C2410C")
        }
        self.current_theme = "Purple"
        
        # Mouse listener
        self.mouse_listener = None
        self.keyboard_listener = None
        self.last_mouse_pos = None
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        ctk.set_appearance_mode("dark")
        
        # Header
        header_frame = ctk.CTkFrame(self.window, fg_color=self.themes[self.current_theme][0], corner_radius=0)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="🎮 FF SENSI PRO", 
            font=("Arial Bold", 28),
            text_color="white"
        )
        title_label.pack(pady=20)
        
        subtitle = ctk.CTkLabel(
            header_frame,
            text="Advanced Free Fire Sensitivity Controller",
            font=("Arial", 12),
            text_color="white"
        )
        subtitle.pack(pady=(0, 15))
        
        # Main container
        main_container = ctk.CTkScrollableFrame(self.window, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20)
        
        # Master Control
        self.create_master_control(main_container)
        
        # Aim Shake Fix
        self.create_aim_shake_section(main_container)
        
        # Aim Smooth
        self.create_aim_smooth_section(main_container)
        
        # Recoil Reduce
        self.create_recoil_section(main_container)
        
        # Smooth Drag
        self.create_smooth_drag_section(main_container)
        
        # Theme Selection
        self.create_theme_section(main_container)
        
        # Footer
        self.create_footer()
        
    def create_master_control(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.themes[self.current_theme][1])
        frame.pack(fill="x", pady=10)
        
        label = ctk.CTkLabel(frame, text="🔥 MASTER CONTROL", font=("Arial Bold", 16))
        label.pack(pady=10)
        
        self.master_btn = ctk.CTkButton(
            frame,
            text="▶ ACTIVATE SENSI",
            font=("Arial Bold", 18),
            height=50,
            fg_color="green",
            hover_color="darkgreen",
            command=self.toggle_master
        )
        self.master_btn.pack(pady=10, padx=20, fill="x")
        
        status_label = ctk.CTkLabel(frame, text="Status: INACTIVE", font=("Arial", 12))
        status_label.pack(pady=(0, 10))
        self.status_label = status_label
        
    def create_aim_shake_section(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=10)
        
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(header, text="🎯 AIM SHAKE FIX", font=("Arial Bold", 14)).pack(side="left")
        
        switch = ctk.CTkSwitch(
            header,
            text="",
            variable=self.aim_shake_fix,
            onvalue=True,
            offvalue=False
        )
        switch.pack(side="right")
        
        slider_frame = ctk.CTkFrame(frame, fg_color="transparent")
        slider_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkLabel(slider_frame, text="Intensity:").pack(side="left", padx=5)
        
        slider = ctk.CTkSlider(
            slider_frame,
            from_=0,
            to=100,
            variable=self.aim_shake_value
        )
        slider.pack(side="left", fill="x", expand=True, padx=10)
        
        value_label = ctk.CTkLabel(slider_frame, text="50%", width=50)
        value_label.pack(side="right")
        
        def update_label(val):
            value_label.configure(text=f"{int(float(val))}%")
        
        slider.configure(command=update_label)
        
    def create_aim_smooth_section(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=10)
        
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(header, text="🎪 AIM SMOOTH", font=("Arial Bold", 14)).pack(side="left")
        
        switch = ctk.CTkSwitch(
            header,
            text="",
            variable=self.aim_smooth,
            onvalue=True,
            offvalue=False
        )
        switch.pack(side="right")
        
        slider_frame = ctk.CTkFrame(frame, fg_color="transparent")
        slider_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkLabel(slider_frame, text="Smoothness:").pack(side="left", padx=5)
        
        slider = ctk.CTkSlider(
            slider_frame,
            from_=0,
            to=100,
            variable=self.aim_smooth_value
        )
        slider.pack(side="left", fill="x", expand=True, padx=10)
        
        value_label = ctk.CTkLabel(slider_frame, text="50%", width=50)
        value_label.pack(side="right")
        
        def update_label(val):
            value_label.configure(text=f"{int(float(val))}%")
        
        slider.configure(command=update_label)
        
    def create_recoil_section(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=10)
        
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(header, text="⚡ RECOIL REDUCE", font=("Arial Bold", 14)).pack(side="left")
        
        switch = ctk.CTkSwitch(
            header,
            text="",
            variable=self.recoil_reduce,
            onvalue=True,
            offvalue=False
        )
        switch.pack(side="right")
        
        slider_frame = ctk.CTkFrame(frame, fg_color="transparent")
        slider_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkLabel(slider_frame, text="Reduction:").pack(side="left", padx=5)
        
        slider = ctk.CTkSlider(
            slider_frame,
            from_=0,
            to=100,
            variable=self.recoil_value
        )
        slider.pack(side="left", fill="x", expand=True, padx=10)
        
        value_label = ctk.CTkLabel(slider_frame, text="50%", width=50)
        value_label.pack(side="right")
        
        def update_label(val):
            value_label.configure(text=f"{int(float(val))}%")
        
        slider.configure(command=update_label)
        
    def create_smooth_drag_section(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=10)
        
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(header, text="✨ SMOOTH DRAG SENSI", font=("Arial Bold", 14)).pack(side="left")
        
        switch = ctk.CTkSwitch(
            header,
            text="",
            variable=self.smooth_drag,
            onvalue=True,
            offvalue=False
        )
        switch.pack(side="right")
        
        slider_frame = ctk.CTkFrame(frame, fg_color="transparent")
        slider_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkLabel(slider_frame, text="Drag Speed:").pack(side="left", padx=5)
        
        slider = ctk.CTkSlider(
            slider_frame,
            from_=0,
            to=100,
            variable=self.drag_smooth_value
        )
        slider.pack(side="left", fill="x", expand=True, padx=10)
        
        value_label = ctk.CTkLabel(slider_frame, text="50%", width=50)
        value_label.pack(side="right")
        
        def update_label(val):
            value_label.configure(text=f"{int(float(val))}%")
        
        slider.configure(command=update_label)
        
    def create_theme_section(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(frame, text="🎨 THEME COLORS", font=("Arial Bold", 14)).pack(pady=10)
        
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        for theme_name, colors in self.themes.items():
            btn = ctk.CTkButton(
                btn_frame,
                text=theme_name,
                fg_color=colors[0],
                hover_color=colors[1],
                width=100,
                command=lambda t=theme_name: self.change_theme(t)
            )
            btn.pack(side="left", padx=5)
            
    def create_footer(self):
        footer = ctk.CTkFrame(self.window, fg_color="transparent")
        footer.pack(side="bottom", fill="x", pady=10)
        
        save_btn = ctk.CTkButton(
            footer,
            text="💾 SAVE SETTINGS",
            command=self.save_settings
        )
        save_btn.pack(side="left", padx=20)
        
        reset_btn = ctk.CTkButton(
            footer,
            text="🔄 RESET ALL",
            fg_color="red",
            hover_color="darkred",
            command=self.reset_settings
        )
        reset_btn.pack(side="right", padx=20)
        
    def toggle_master(self):
        self.is_active = not self.is_active
        
        if self.is_active:
            self.master_btn.configure(
                text="⏸ DEACTIVATE SENSI",
                fg_color="red",
                hover_color="darkred"
            )
            self.status_label.configure(text="Status: ACTIVE ✓")
            self.start_listeners()
        else:
            self.master_btn.configure(
                text="▶ ACTIVATE SENSI",
                fg_color="green",
                hover_color="darkgreen"
            )
            self.status_label.configure(text="Status: INACTIVE")
            self.stop_listeners()
            
    def start_listeners(self):
        self.mouse_listener = mouse.Listener(
            on_move=self.on_mouse_move,
            on_click=self.on_mouse_click
        )
        self.mouse_listener.start()
        
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press
        )
        self.keyboard_listener.start()
        
    def stop_listeners(self):
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            
    def on_mouse_move(self, x, y):
        if not self.is_active:
            return
            
        if self.last_mouse_pos is None:
            self.last_mouse_pos = (x, y)
            return
            
        dx = x - self.last_mouse_pos[0]
        dy = y - self.last_mouse_pos[1]
        
        # Apply aim shake fix
        if self.aim_shake_fix.get():
            shake_factor = (100 - self.aim_shake_value.get()) / 100
            dx = int(dx * shake_factor)
            dy = int(dy * shake_factor)
            
        # Apply aim smooth
        if self.aim_smooth.get():
            smooth_factor = self.aim_smooth_value.get() / 100
            dx = int(dx * smooth_factor)
            dy = int(dy * smooth_factor)
            
        # Apply smooth drag
        if self.smooth_drag.get():
            drag_factor = self.drag_smooth_value.get() / 100
            dx = int(dx * drag_factor)
            dy = int(dy * drag_factor)
            
        self.last_mouse_pos = (x, y)
        
    def on_mouse_click(self, x, y, button, pressed):
        if not self.is_active or not self.recoil_reduce.get():
            return
            
        if pressed and button == mouse.Button.left:
            # Apply recoil reduction
            threading.Thread(target=self.apply_recoil_compensation, daemon=True).start()
            
    def apply_recoil_compensation(self):
        recoil_amount = int(self.recoil_value.get() / 10)
        for i in range(recoil_amount):
            ctypes.windll.user32.mouse_event(1, 0, 2, 0, 0)
            time.sleep(0.01)
            
    def on_key_press(self, key):
        pass
        
    def change_theme(self, theme_name):
        self.current_theme = theme_name
        self.window.destroy()
        self.__init__()
        self.run()
        
    def save_settings(self):
        settings = {
            "aim_shake_fix": self.aim_shake_fix.get(),
            "aim_smooth": self.aim_smooth.get(),
            "recoil_reduce": self.recoil_reduce.get(),
            "smooth_drag": self.smooth_drag.get(),
            "aim_shake_value": self.aim_shake_value.get(),
            "aim_smooth_value": self.aim_smooth_value.get(),
            "recoil_value": self.recoil_value.get(),
            "drag_smooth_value": self.drag_smooth_value.get(),
            "theme": self.current_theme
        }
        
        with open("ff_sensi_settings.json", "w") as f:
            json.dump(settings, f)
            
        messagebox.showinfo("Success", "Settings saved successfully!")
        
    def load_settings(self):
        try:
            if os.path.exists("ff_sensi_settings.json"):
                with open("ff_sensi_settings.json", "r") as f:
                    settings = json.load(f)
                    
                self.aim_shake_fix.set(settings.get("aim_shake_fix", False))
                self.aim_smooth.set(settings.get("aim_smooth", False))
                self.recoil_reduce.set(settings.get("recoil_reduce", False))
                self.smooth_drag.set(settings.get("smooth_drag", False))
                self.aim_shake_value.set(settings.get("aim_shake_value", 50))
                self.aim_smooth_value.set(settings.get("aim_smooth_value", 50))
                self.recoil_value.set(settings.get("recoil_value", 50))
                self.drag_smooth_value.set(settings.get("drag_smooth_value", 50))
                self.current_theme = settings.get("theme", "Purple")
        except:
            pass
            
    def reset_settings(self):
        if messagebox.askyesno("Reset", "Are you sure you want to reset all settings?"):
            self.aim_shake_fix.set(False)
            self.aim_smooth.set(False)
            self.recoil_reduce.set(False)
            self.smooth_drag.set(False)
            self.aim_shake_value.set(50)
            self.aim_smooth_value.set(50)
            self.recoil_value.set(50)
            self.drag_smooth_value.set(50)
            messagebox.showinfo("Success", "All settings reset!")
            
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = FFSensiApp()
    app.run()