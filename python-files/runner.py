import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class CustomMessageBox:
    def __init__(self, parent, title, message, button_text):
        self.parent = parent
        self.title = title
        self.message = message
        self.button_text = button_text
        self.result = None
        self.create_widgets()

    def create_widgets(self):
        self.top = tk.Toplevel(self.parent)
        self.top.title(self.title)
        self.top.grab_set()  # Make this window modal (blocks interaction with other windows)
        
        # Get screen width and height
        screen_width = self.top.winfo_screenwidth()
        screen_height = self.top.winfo_screenheight()
        
        # Define the size of the dialog
        dialog_width = 300
        dialog_height = 150
        
        # Calculate position
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        
        # Set the geometry of the dialog
        self.top.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Make the dialog always on top
        self.top.attributes('-topmost', True)
        
        # Message Label
        self.message_label = tk.Label(self.top, text=self.message, padx=20, pady=20)
        self.message_label.pack()

        # Button
        self.ok_button = tk.Button(self.top, text=self.button_text, command=self.on_ok, padx=10, pady=5)
        self.ok_button.pack()

    def on_ok(self):
        self.result = 'ok'
        self.top.destroy()

    def show(self):
        self.parent.wait_window(self.top)
        return self.result


def show_custom_message(parent, title, message, button_text):
    dialog = CustomMessageBox(parent, title, message, button_text)
    return dialog.show()

def check_password():
    if password_entry.get().upper() == "SIMP":  # Replace with your password
        root.destroy()  # Close the window
    else:
        show_custom_message(root, "Error", "Incorrect password!", "Shit!")

def on_enter_key(event):
    check_password()  # Call the function to check the password

def block_alt_tab(event):
    # Prevent Alt-Tab from working
    return "break"


def prevent_close():
    # Show a message box or an alert when attempting to close
    # messagebox.showwarning("Warning", "OH a smart one, huh?")
    show_custom_message(root, "Warning", "Smart one, huh?", "Fuck you!")
    # Prevent the window from being closed
    return "break"

def setup_window(root):
    # Set the window to fullscreen
    root.attributes('-fullscreen', True)

    # Set the window to be transparent
    root.wm_attributes('-alpha', 1)  # Adjust alpha for transparency level
    root.wm_attributes('-topmost', True)  # Keep the window on top

    # Load and display the image
    image = Image.open('D-MN.png')  # Replace with your image path
    photo = ImageTk.PhotoImage(image)

    # Create a frame to contain both the image and the form
    container = tk.Frame(root, bg='black')
    container.place(relx=0.5, rely=0.5, anchor='center')

    # Add the image to the frame
    img_label = tk.Label(container, image=photo, bg='black')
    img_label.photo = photo  # Keep a reference to avoid garbage collection
    img_label.pack(pady=0)  # Add some padding around the image

    # Create the password entry form below the image
    form_frame = tk.Frame(container, bg='black')
    form_frame.pack(pady=(0, 180))  # Padding at the top and bottom of the form

    tk.Label(form_frame, text="Enter Password:", bg='black', fg="red", font=20).pack(pady=5)
    global password_entry
    password_entry = tk.Entry(form_frame, show="*", bg='black', border=2, fg="red", font=20)
    password_entry.pack(pady=5)


    # Bind Enter key to submit form
    root.bind('<Return>', on_enter_key)

    # Bind Alt-Tab blocking (this will prevent Alt-Tab only within the app window)
    root.bind('<Alt-Tab>', block_alt_tab)
    
    # Optionally bind other key combinations to block them (example)
    root.bind('<Alt_L>', block_alt_tab)
    root.bind('<Alt_R>', block_alt_tab)
    # Bind the escape key to exit fullscreen (optional)
    root.bind('<Escape>', lambda e: root.attributes('-fullscreen', False))

        # Override the window close button behavior and other close attempts
    root.protocol("WM_DELETE_WINDOW", prevent_close)  # Prevent closing via X button
    root.bind_all('<Alt-Tab>', prevent_close)         # Attempt to block Alt-Tab
    root.bind_all('<Alt_L>', prevent_close)           # Block Alt key (left)
    root.bind_all('<Alt_R>', prevent_close)           # Block Alt key (right)

def main():
    global root
    root = tk.Tk()
    setup_window(root)
    root.mainloop()

if __name__ == "__main__":
    main()
