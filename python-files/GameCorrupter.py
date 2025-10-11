import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, scrolledtext
import zipfile
import os
import shutil

class AppModifier(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File Modifier Tool (for ZIP archives)")
        self.geometry("800x600")

        # --- Member Variables ---
        self.original_filepath = None
        self.backup_filepath = None
        # This dictionary will hold the file data in memory
        self.archive_data = {} 

        # --- UI Setup ---
        # Top Frame for controls
        top_frame = tk.Frame(self, padx=10, pady=10)
        top_frame.pack(fill=tk.X)

        self.load_button = tk.Button(top_frame, text="Load .EXE (Select a ZIP file)", command=self.load_file)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(top_frame, text="Save Changes", state=tk.DISABLED, command=self.save_changes)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        self.restore_button = tk.Button(top_frame, text="Restore Original", state=tk.DISABLED, command=self.restore_original)
        self.restore_button.pack(side=tk.LEFT, padx=5)

        # Main content frame
        main_frame = tk.Frame(self, padx=10, pady=5)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_columnconfigure(1, weight=3) # Make the right column (text area) wider
        main_frame.grid_rowconfigure(0, weight=1)

        # Left side: File list
        list_frame = tk.Frame(main_frame, bd=1, relief=tk.SUNKEN)
        list_frame.grid(row=0, column=0, sticky="nswe", padx=(0, 5))
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.file_listbox = tk.Listbox(list_frame)
        self.file_listbox.grid(row=0, column=0, sticky="nswe")

        # Add a scrollbar to the listbox
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        # Right side: Search and display
        search_frame = tk.Frame(main_frame)
        search_frame.grid(row=0, column=1, sticky="nswe")
        search_frame.grid_columnconfigure(0, weight=1)
        search_frame.grid_rowconfigure(1, weight=1)

        # Value Search box
        search_controls_frame = tk.Frame(search_frame)
        search_controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        search_controls_frame.grid_columnconfigure(1, weight=1)

        tk.Label(search_controls_frame, text="Value Search:").grid(row=0, column=0, padx=(0, 5))
        self.search_entry = tk.Entry(search_controls_frame)
        self.search_entry.grid(row=0, column=1, sticky="ew")
        self.search_button = tk.Button(search_controls_frame, text="Find", state=tk.DISABLED, command=self.search_values)
        self.search_button.grid(row=0, column=2, padx=(5, 0))

        # Text area for search results
        self.search_results_text = scrolledtext.ScrolledText(search_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.search_results_text.grid(row=1, column=0, sticky="nswe")

        # --- Context Menu for Listbox ---
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Delete File", command=self.delete_file)
        self.context_menu.add_command(label="Delete What's Inside (Blank File)", command=self.blank_file_content)
        
        self.file_listbox.bind("<Button-3>", self.show_context_menu)

    def load_file(self):
        """Opens a file dialog to select a ZIP and loads its contents."""
        filepath = filedialog.askopenfilename(
            title="Select a file to modify",
            filetypes=[("ZIP archives", "*.zip"), ("All files", "*.*")]
        )
        if not filepath:
            return

        self.original_filepath = filepath
        self.backup_filepath = self.original_filepath + ".bak"
        
        # Create a backup
        try:
            shutil.copy2(self.original_filepath, self.backup_filepath)
        except Exception as e:
            messagebox.showerror("Backup Error", f"Could not create a backup file.\nError: {e}")
            return
            
        # Read the zip file into our in-memory dictionary
        try:
            with zipfile.ZipFile(self.original_filepath, 'r') as zf:
                for filename in zf.namelist():
                    self.archive_data[filename] = zf.read(filename)
        except zipfile.BadZipFile:
            messagebox.showerror("Error", "The selected file is not a valid ZIP archive.")
            os.remove(self.backup_filepath) # Clean up failed backup
            return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file.\nError: {e}")
            os.remove(self.backup_filepath) # Clean up failed backup
            return
            
        self.update_ui_after_load()
        messagebox.showinfo("Success", f"File loaded and backup created at:\n{self.backup_filepath}")

    def update_ui_after_load(self):
        """Refreshes the UI elements after a file has been loaded or modified."""
        self.file_listbox.delete(0, tk.END)
        for filename in sorted(self.archive_data.keys()):
            self.file_listbox.insert(tk.END, filename)
        
        self.save_button.config(state=tk.NORMAL)
        self.restore_button.config(state=tk.NORMAL)
        self.search_button.config(state=tk.NORMAL)
        self.search_results_text.config(state=tk.NORMAL)
        self.search_results_text.delete('1.0', tk.END)
        self.search_results_text.config(state=tk.DISABLED)

    def show_context_menu(self, event):
        """Displays the right-click context menu."""
        selection = self.file_listbox.curselection()
        if selection:
            self.file_listbox.selection_clear(0, tk.END)
            self.file_listbox.selection_set(selection[0])
            self.context_menu.post(event.x_root, event.y_root)

    def delete_file(self):
        """Deletes the selected file from the in-memory dictionary."""
        selection_index = self.file_listbox.curselection()
        if not selection_index:
            return
            
        filename = self.file_listbox.get(selection_index[0])
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{filename}'?"):
            del self.archive_data[filename]
            self.update_ui_after_load()

    def blank_file_content(self):
        """Replaces the content of the selected file with empty bytes."""
        selection_index = self.file_listbox.curselection()
        if not selection_index:
            return

        filename = self.file_listbox.get(selection_index[0])
        if messagebox.askyesno("Confirm Blank", f"Are you sure you want to delete the contents of '{filename}'?"):
            self.archive_data[filename] = b'' # Set to empty bytes
            messagebox.showinfo("Success", f"Contents of '{filename}' have been blanked.")

    def search_values(self):
        """Searches for a string in all file contents."""
        query = self.search_entry.get()
        if not query:
            return
        
        self.search_results_text.config(state=tk.NORMAL)
        self.search_results_text.delete('1.0', tk.END)
        self.search_results_text.insert(tk.END, f"Searching for: '{query}'\n" + "="*40 + "\n\n")

        found = False
        try:
            # Try searching as bytes
            query_bytes = query.encode('utf-8')
        except UnicodeEncodeError:
            self.search_results_text.insert(tk.END, "Error: Search query contains characters that cannot be encoded.")
            self.search_results_text.config(state=tk.DISABLED)
            return

        for filename, content in self.archive_data.items():
            if query_bytes in content:
                found = True
                self.search_results_text.insert(tk.END, f"Found in: {filename}\n---\n")
                # To avoid printing gibberish, we'll try to decode and show context
                try:
                    content_str = content.decode('utf-8', errors='ignore')
                    for line_num, line in enumerate(content_str.splitlines()):
                        if query in line:
                            self.search_results_text.insert(tk.END, f"  Line {line_num + 1}: {line.strip()}\n")
                except Exception:
                    self.search_results_text.insert(tk.END, "  (Content is binary and cannot be displayed as text)\n")
                self.search_results_text.insert(tk.END, "\n")
        
        if not found:
            self.search_results_text.insert(tk.END, "No matches found.")

        self.search_results_text.config(state=tk.DISABLED)

    def save_changes(self):
        """Saves the contents of the in-memory dictionary back to the original file path."""
        if not self.original_filepath:
            return
        
        try:
            with zipfile.ZipFile(self.original_filepath, 'w') as zf:
                for filename, content in self.archive_data.items():
                    zf.writestr(filename, content)
            messagebox.showinfo("Success", "All changes have been saved.")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save the file.\nError: {e}")

    def restore_original(self):
        """Restores the original file from the backup."""
        if not self.backup_filepath or not os.path.exists(self.backup_filepath):
            messagebox.showerror("Error", "No backup file found to restore from.")
            return

        if messagebox.askyesno("Confirm Restore", "Are you sure you want to discard all changes and restore the original file?"):
            try:
                # We need to reset our in-memory state as well
                self.archive_data.clear()
                shutil.copy2(self.backup_filepath, self.original_filepath)
                # Reload the restored data back into the app
                with zipfile.ZipFile(self.original_filepath, 'r') as zf:
                    for filename in zf.namelist():
                        self.archive_data[filename] = zf.read(filename)
                self.update_ui_after_load()
                messagebox.showinfo("Success", "Original file has been restored.")
            except Exception as e:
                messagebox.showerror("Restore Error", f"Could not restore the file.\nError: {e}")


if __name__ == "__main__":
    app = AppModifier()
    app.mainloop()