
"""
library_marathi_fixed.py

A corrected and improved single-file library management Tkinter app with Marathi UI.
Features:
- Import from .csv, .xlsx, .xls (uses pandas)
- Export to .xlsx (openpyxl recommended) or .csv
- Internal UUID used for safe edit/delete
- Search (vectorized), add, edit, delete (multi-select)
- Basic validation for Year and BookID
- Friendly Marathi messages and status bar

Note: Requires pandas. For Excel read/write, install openpyxl and xlrd if needed:
    pip install pandas openpyxl xlrd
Run: python3 library_marathi_fixed.py
"""
import os
import sys
import uuid
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog

# Try to import pandas lazily and show helpful messages if missing.
try:
    import pandas as pd
except Exception as e:
    pd = None

# Default visible columns (Marathi labels kept as keys in code for clarity)
DEFAULT_COLUMNS = ["BookID", "Title", "Author", "Year", "Publisher"]

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("लायब्ररी मॅनेजर (मराठी)")
        self.df = pd.DataFrame(columns=["_uuid"] + DEFAULT_COLUMNS) if pd is not None else None

        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.build_ui()
        self.set_status("तयार")

    def build_ui(self):
        frm = ttk.Frame(self.root, padding=8)
        frm.pack(fill="both", expand=True)

        topbar = ttk.Frame(frm)
        topbar.pack(fill="x", pady=4)
        ttk.Label(topbar, text="शोध:").pack(side="left")
        search_entry = ttk.Entry(topbar, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=4)
        search_entry.bind("<KeyRelease>", lambda e: self.refresh_table())

        btn_frame = ttk.Frame(topbar)
        btn_frame.pack(side="right")
        ttk.Button(btn_frame, text="फाईल आयात करा", command=self.load_excel).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="जतन करा", command=self.save_file).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="नवीन नोंद", command=self.add_record).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="संपादित करा", command=self.edit_selected).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="हटवा", command=self.delete_selected).pack(side="left", padx=2)

        # Treeview
        cols = DEFAULT_COLUMNS
        self.tree = ttk.Treeview(frm, columns=cols, show="headings", selectmode="extended")
        for c in cols:
            self.tree.heading(c, text=c, command=lambda _c=c: self.sort_by_column(_c, False))
            self.tree.column(c, width=120, anchor="w")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda e: self.edit_selected())

        # Status bar
        status = ttk.Label(self.root, textvariable=self.status_var, anchor="w")
        status.pack(fill="x", side="bottom")

    def set_status(self, msg):
        self.status_var.set(msg)

    def ensure_pandas(self):
        if pd is None:
            messagebox.showerror("पुस्तकालय अॅप", "हे स्क्रिप्ट चालवण्यासाठी 'pandas' लागेल.\nकृपया pip install pandas करा आणि पुन्हा चालवा.")
            return False
        return True

    def load_excel(self):
        if not self.ensure_pandas():
            return
        path = filedialog.askopenfilename(title="CSV/Excel फाइल निवडा", filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files", "*.*")])
        if not path:
            return
        try:
            if path.lower().endswith((".xlsx", ".xls")):
                df_in = pd.read_excel(path)
            else:
                df_in = pd.read_csv(path)
        except Exception as e:
            messagebox.showerror("त्रुटी", f"फाइल वाचताना त्रुटी: {e}")
            return

        # Ask for column mapping if columns don't match
        mapping = self.ask_column_mapping(list(df_in.columns), DEFAULT_COLUMNS)
        if mapping is None:
            self.set_status("कॉलम मॅपिंग रद्द")
            return

        new_rows = []
        for _, row in df_in.iterrows():
            obj = {"_uuid": str(uuid.uuid4())}
            for tgt in DEFAULT_COLUMNS:
                src = mapping.get(tgt)
                if src and src in df_in.columns:
                    val = row[src]
                    if pd.isna(val):
                        val = ""
                    obj[tgt] = str(val)
                else:
                    obj[tgt] = ""
            new_rows.append(obj)

        self.df = pd.DataFrame(new_rows)
        self.set_status(f"फाइल आयात पूर्ण — {len(self.df)} रेकॉर्ड")
        self.refresh_table()

    def ask_column_mapping(self, src_cols, target_cols):
        """
        Show a dialog to map source columns to target columns.
        Returns dict mapping target_col -> source_col (or None if cancelled).
        """
        dialog = tk.Toplevel(self.root)
        dialog.title("कॉलम मॅपिंग")
        dialog.grab_set()

        mappings = {}
        vars_map = {}
        ttk.Label(dialog, text="स्रोत कॉलम").grid(row=0, column=0, padx=6, pady=6)
        ttk.Label(dialog, text="लक्ष्य कॉलम").grid(row=0, column=1, padx=6, pady=6)
        for i, tgt in enumerate(target_cols, start=1):
            ttk.Label(dialog, text=tgt).grid(row=i, column=0, sticky="w", padx=6, pady=3)
            var = tk.StringVar(value=src_cols[0] if src_cols else "")
            vars_map[tgt] = var
            opt = ttk.Combobox(dialog, values=["(रिक्त)"] + src_cols, textvariable=var, state="readonly")
            opt.grid(row=i, column=1, padx=6, pady=3)
            opt.set(src_cols[i-1] if i-1 < len(src_cols) else "(रिक्त)")

        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=len(target_cols)+1, column=0, columnspan=2, pady=8)
        result = {"ok": False}

        def on_ok():
            for tgt in target_cols:
                val = vars_map[tgt].get()
                result[tgt] = None if val == "(रिक्त)" else val
            result["ok"] = True
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        ttk.Button(btn_frame, text="ठीक आहे", command=on_ok).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="रद्द करा", command=on_cancel).pack(side="left", padx=6)
        dialog.wait_window()
        return None if not result.get("ok") else {t: result[t] for t in target_cols}

    def refresh_table(self):
        # clear
        for r in self.tree.get_children():
            self.tree.delete(r)
        if self.df is None:
            return
        q = self.search_var.get().strip().lower()
        df = self.df.copy()

        if q:
            # vectorized mask across visible columns
            mask = pd.Series(False, index=df.index)
            for c in DEFAULT_COLUMNS:
                mask = mask | df[c].astype(str).str.lower().str.contains(q, na=False)
            df = df[mask]

        for _, row in df.iterrows():
            values = [row.get(c, "") for c in DEFAULT_COLUMNS]
            # use uuid as iid so edits/deletes are reliable
            iid = row["_uuid"]
            self.tree.insert("", "end", iid=iid, values=values)

        self.set_status(f"{len(df)} रेकॉर्ड दाखवत आहेत")

    def save_file(self):
        if not self.ensure_pandas():
            return
        if self.df is None or len(self.df) == 0:
            messagebox.showinfo("जतन", "जतन करण्यासाठी कोणतेही रेकॉर्ड नाहीत.")
            return
        path = filedialog.asksaveasfilename(title="जतन करा", defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx"), ("CSV file", "*.csv")])
        if not path:
            return
        try:
            export_df = self.df.drop(columns=["_uuid"])
            if path.lower().endswith(".csv"):
                export_df.to_csv(path, index=False)
            else:
                # try to let pandas choose engine; openpyxl will be used for .xlsx if available
                export_df.to_excel(path, index=False)
            self.set_status(f"फाइल जतन केली: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("त्रुटी", f"फाइल जतन करताना त्रुटी: {e}")

    def add_record(self):
        if not self.ensure_pandas():
            return
        data = self.ask_record_dialog()
        if not data:
            return
        # validation
        if not data["BookID"].strip():
            messagebox.showwarning("वैधता", "BookID रिक्त ठेवू नका.")
            return
        if data["Year"]:
            try:
                _ = int(data["Year"])
            except:
                messagebox.showwarning("वैधता", "Year मध्ये पूर्णांक द्या.")
                return
        # append
        row = {"_uuid": str(uuid.uuid4())}
        for c in DEFAULT_COLUMNS:
            row[c] = data.get(c, "")
        self.df = pd.concat([self.df, pd.DataFrame([row])], ignore_index=True)
        self.refresh_table()
        self.set_status("नवीन नोंद जोडली")

    def ask_record_dialog(self, existing=None):
        """
        existing: dict with DEFAULT_COLUMNS keys if editing
        returns dict or None
        """
        dialog = tk.Toplevel(self.root)
        dialog.title("नोंद" + (" संपादित करा" if existing else " जोडा"))
        dialog.grab_set()
        vars = {}
        for i, c in enumerate(DEFAULT_COLUMNS):
            ttk.Label(dialog, text=c).grid(row=i, column=0, padx=6, pady=4, sticky="w")
            v = tk.StringVar(value=(existing.get(c, "") if existing else ""))
            vars[c] = v
            ttk.Entry(dialog, textvariable=v, width=40).grid(row=i, column=1, padx=6, pady=4)

        result = {"ok": False}
        def on_ok():
            result.update({c: vars[c].get() for c in DEFAULT_COLUMNS})
            result["ok"] = True
            dialog.destroy()
        def on_cancel():
            dialog.destroy()
        btnf = ttk.Frame(dialog)
        btnf.grid(row=len(DEFAULT_COLUMNS), column=0, columnspan=2, pady=8)
        ttk.Button(btnf, text="ठीक आहे", command=on_ok).pack(side="left", padx=6)
        ttk.Button(btnf, text="रद्द करा", command=on_cancel).pack(side="left", padx=6)
        dialog.wait_window()
        return None if not result.get("ok") else {c: result[c] for c in DEFAULT_COLUMNS}

    def get_selected_uuids(self):
        sel = self.tree.selection()
        return list(sel)

    def edit_selected(self):
        if self.df is None:
            return
        uuids = self.get_selected_uuids()
        if not uuids:
            messagebox.showinfo("निवड", "सर्वप्रथम एक नोंद निवडा.")
            return
        if len(uuids) > 1:
            messagebox.showinfo("निवड", "केवळ एक नोंद संपादित करा किंवा प्रथम एक निवडा.")
            return
        uid = uuids[0]
        row = self.df[self.df["_uuid"] == uid].iloc[0].to_dict()
        existing = {c: row.get(c, "") for c in DEFAULT_COLUMNS}
        data = self.ask_record_dialog(existing=existing)
        if not data:
            return
        # validate
        if not data["BookID"].strip():
            messagebox.showwarning("वैधता", "BookID रिक्त ठेवू नका.")
            return
        if data["Year"]:
            try:
                _ = int(data["Year"])
            except:
                messagebox.showwarning("वैधता", "Year मध्ये पूर्णांक द्या.")
                return
        # update df
        for c in DEFAULT_COLUMNS:
            self.df.loc[self.df["_uuid"] == uid, c] = data.get(c, "")
        self.refresh_table()
        self.set_status("नोंद संपादित केली")

    def delete_selected(self):
        if self.df is None:
            return
        uuids = self.get_selected_uuids()
        if not uuids:
            messagebox.showinfo("निवड नाही", "सर्वप्रथम नोंदी निवडा.")
            return
        if not messagebox.askyesno("काय खात्री?", f"{len(uuids)} नोंदी कायमस्वरूपी हटवायच्या का?"):
            return
        self.df = self.df[~self.df["_uuid"].isin(uuids)].reset_index(drop=True)
        self.refresh_table()
        self.set_status(f"{len(uuids)} नोंदी हटवल्या")

    def sort_by_column(self, col, reverse):
        if self.df is None:
            return
        self.df = self.df.sort_values(by=col, ascending=not reverse).reset_index(drop=True)
        self.refresh_table()
        # Toggle next time
        # Rebind header command
        self.tree.heading(col, command=lambda: self.sort_by_column(col, not reverse))

def main():
    root = tk.Tk()
    app = LibraryApp(root)
    root.geometry("800x500")
    root.mainloop()

if __name__ == "__main__":
    main()
