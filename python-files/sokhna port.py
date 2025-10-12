"""
Company Manager - Final Version (Python + PyQt5 + SQLite)
Features:
- SQLite DB (company_data.db) with tables: companies, items, inspections, notes
- Config file (config.json) for base folder selection (attachments + backup)
- PyQt5 GUI: Companies list, Company details (items), date pickers, colored rows
- Attachments: copy to attachments/<company_name>/ and store path in DB
- Open attachments with default OS app
- Auto-save on edits (cellChanged / widget signals)
- Auto backup (light) after major edits
- Export company data to Excel (pandas)

Run: python company_manager_main.py
Requires: PyQt5, pandas

"""

import sys
import os
import json
import shutil
import sqlite3
from datetime import datetime, date
from functools import partial

from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QFileDialog, QMessageBox,
    QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QAction, QSplitter, QDateEdit, QFormLayout, QComboBox,
    QTextEdit, QHeaderView
)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QColor

# Optional dependency
try:
    import pandas as pd
except Exception:
    pd = None

CONFIG_FILE = "config.json"
DB_FILE = "company_data.db"
AUTO_BACKUP_AFTER_EDIT_SECONDS = 2  # debounce time for auto-backup after edits

# ----------------------- Database utilities -----------------------

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        manager TEXT,
        safety_officer TEXT,
        total_evaluation REAL DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        item_name TEXT,
        issue_date TEXT,
        review_date TEXT,
        status TEXT,
        evaluation_percent REAL,
        ignored INTEGER DEFAULT 0,
        attachment TEXT,
        FOREIGN KEY(company_id) REFERENCES companies(id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS inspections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        inspection_date TEXT,
        report TEXT,
        total_notes INTEGER,
        fixed_notes INTEGER,
        remaining_notes INTEGER,
        FOREIGN KEY(company_id) REFERENCES companies(id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inspection_id INTEGER,
        note_text TEXT,
        status TEXT,
        FOREIGN KEY(inspection_id) REFERENCES inspections(id)
    )
    """)

    conn.commit()
    conn.close()


# ----------------------- Config utilities -----------------------

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_config(cfg: dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


# ----------------------- Backup utilities -----------------------

def ensure_base_folders(base_folder):
    attachments = os.path.join(base_folder, "attachments")
    backup = os.path.join(base_folder, "backup")
    os.makedirs(attachments, exist_ok=True)
    os.makedirs(backup, exist_ok=True)
    return attachments, backup


def auto_backup_db(base_folder):
    backup_folder = os.path.join(base_folder, "backup")
    os.makedirs(backup_folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(backup_folder, f"auto_backup_{timestamp}.db")
    try:
        shutil.copy(DB_FILE, dest)
        print("Auto-backup created:", dest)
    except Exception as e:
        print("Auto-backup failed:", e)


# ----------------------- Core App -----------------------

class CompanyManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Company Manager - نهائي")
        self.resize(1100, 700)

        init_db()

        self.cfg = load_config()
        self.base_folder = self.cfg.get("base_folder")
        if not self.base_folder or not os.path.exists(self.base_folder):
            self.select_base_folder(first_time=True)
        else:
            ensure_base_folders(self.base_folder)

        # UI elements
        self.companies_table = QTableWidget()
        self.items_table = QTableWidget()

        self.company_search = QLineEdit()
        self.add_company_btn = QPushButton("إضافة شركة")
        self.delete_company_btn = QPushButton("حذف الشركة المختارة")

        self.export_btn = QPushButton("تصدير شركة إلى Excel")
        self.backup_btn = QPushButton("إنشاء نسخة احتياطية الآن")

        # For auto backup debounce
        self._backup_timer = QTimer()
        self._backup_timer.setSingleShot(True)
        self._backup_timer.timeout.connect(self._perform_auto_backup)

        self._setup_ui()
        self.load_companies()

    def select_base_folder(self, first_time=False):
        folder = QFileDialog.getExistingDirectory(self, "اختر المجلد الرئيسي لتخزين البيانات والمرفقات")
        if not folder:
            if first_time:
                QMessageBox.critical(self, "تنبيه", "يجب اختيار مجلد رئيسي لتخزين البيانات. البرنامج سيغلق.")
                sys.exit(0)
            return
        self.base_folder = folder
        ensure_base_folders(self.base_folder)
        self.cfg["base_folder"] = self.base_folder
        save_config(self.cfg)

    def _setup_ui(self):
        # Menu
        menubar = self.menuBar()
        settings_menu = menubar.addMenu("الإعدادات")
        change_base_action = QAction("تغيير المجلد الرئيسي", self)
        change_base_action.triggered.connect(self.change_base_folder)
        settings_menu.addAction(change_base_action)

        # Top controls
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("بحث: "))
        top_layout.addWidget(self.company_search)
        top_layout.addWidget(self.add_company_btn)
        top_layout.addWidget(self.delete_company_btn)
        top_layout.addWidget(self.export_btn)
        top_layout.addWidget(self.backup_btn)

        self.add_company_btn.clicked.connect(self.add_company_dialog)
        self.delete_company_btn.clicked.connect(self.delete_selected_company)
        self.export_btn.clicked.connect(self.export_selected_company)
        self.backup_btn.clicked.connect(self.manual_backup)

        self.company_search.textChanged.connect(self.load_companies)

        # Companies table setup
        self.companies_table.setColumnCount(5)
        self.companies_table.setHorizontalHeaderLabels(["ID", "اسم الشركة", "المدير", "مسئول السلامة", "تقييم %"])
        self.companies_table.verticalHeader().setVisible(False)
        self.companies_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.companies_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.companies_table.cellClicked.connect(self.on_company_selected)
        self.companies_table.setColumnHidden(0, True)
        self.companies_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Items table setup
        self.items_table.setColumnCount(9)
        self.items_table.setHorizontalHeaderLabels(["ID", "البند", "تاريخ الإصدار", "تاريخ المراجعة", "الموقف", "نسبة %", "تجاهل", "مرفق", "فتح"])
        self.items_table.verticalHeader().setVisible(False)
        self.items_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.items_table.setColumnHidden(0, True)
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Allow edits for some columns
        self.items_table.itemChanged.connect(self.on_item_cell_changed)

        # Layout main
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.addLayout(top_layout)
        left_layout.addWidget(QLabel("قائمة الشركات"))
        left_layout.addWidget(self.companies_table)
        left_widget.setLayout(left_layout)

        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("بنود الشركة"))
        right_layout.addWidget(self.items_table)
        right_widget.setLayout(right_layout)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)

        central = QWidget()
        central_layout = QVBoxLayout()
        central_layout.addWidget(splitter)
        central.setLayout(central_layout)

        self.setCentralWidget(central)

    # ----------------------- Companies -----------------------
    def load_companies(self):
        term = self.company_search.text().strip()
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        if term:
            cur.execute("SELECT id, name, manager, safety_officer, total_evaluation FROM companies WHERE name LIKE ? ORDER BY name", (f"%{term}%",))
        else:
            cur.execute("SELECT id, name, manager, safety_officer, total_evaluation FROM companies ORDER BY name")
        rows = cur.fetchall()
        conn.close()

        self.companies_table.blockSignals(True)
        self.companies_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, v in enumerate(row):
                it = QTableWidgetItem(str(v) if v is not None else "")
                if j == 0:
                    it.setData(Qt.UserRole, v)
                self.companies_table.setItem(i, j, it)
        self.companies_table.blockSignals(False)

        # select first
        if rows:
            self.companies_table.selectRow(0)
            self.on_company_selected(0, 0)
        else:
            self.items_table.setRowCount(0)

    def on_company_selected(self, row, column):
        it = self.companies_table.item(row, 0)
        if not it:
            return
        company_id = int(it.text())
        self.current_company_id = company_id
        self.current_company_name = self.companies_table.item(row, 1).text()
        self.load_items(company_id)

    def add_company_dialog(self):
        dlg = QWidget()
        dlg.setWindowTitle("إضافة شركة")
        layout = QFormLayout()
        name_edit = QLineEdit()
        manager_edit = QLineEdit()
        safety_edit = QLineEdit()
        layout.addRow("اسم الشركة:", name_edit)
        layout.addRow("مدير المنشأة:", manager_edit)
        layout.addRow("مسئول السلامة:", safety_edit)
        btn = QPushButton("إضافة")

        def do_add():
            name = name_edit.text().strip()
            if not name:
                QMessageBox.warning(dlg, "خطأ", "ادخل اسم الشركة.")
                return
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            try:
                cur.execute("INSERT INTO companies (name, manager, safety_officer) VALUES (?, ?, ?)", (name, manager_edit.text(), safety_edit.text()))
                conn.commit()
            except sqlite3.IntegrityError:
                QMessageBox.warning(dlg, "مكرر", "اسم الشركة موجود بالفعل.")
                conn.close()
                return
            conn.close()
            dlg.close()
            self.load_companies()
            # make attachments folder
            attachments_dir = os.path.join(self.base_folder, 'attachments', name)
            os.makedirs(attachments_dir, exist_ok=True)
            # auto backup
            self.trigger_auto_backup()

        btn.clicked.connect(do_add)
        layout.addWidget(btn)
        dlg.setLayout(layout)
        dlg.show()

    def delete_selected_company(self):
        sel = self.companies_table.currentRow()
        if sel < 0:
            return
        cid = int(self.companies_table.item(sel, 0).text())
        name = self.companies_table.item(sel, 1).text()
        res = QMessageBox.question(self, "تأكيد", f"هل تريد حذف الشركة {name} ومحتوياتها؟\n(سيتم حذف السجلات فقط، المرفقات ستظل في المجلد)")
        if res != QMessageBox.Yes:
            return
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("DELETE FROM notes WHERE inspection_id IN (SELECT id FROM inspections WHERE company_id=?)", (cid,))
        cur.execute("DELETE FROM inspections WHERE company_id=?", (cid,))
        cur.execute("DELETE FROM items WHERE company_id=?", (cid,))
        cur.execute("DELETE FROM companies WHERE id=?", (cid,))
        conn.commit()
        conn.close()
        self.load_companies()
        self.trigger_auto_backup()

    # ----------------------- Items -----------------------
    def load_items(self, company_id):
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT id, item_name, issue_date, review_date, status, evaluation_percent, ignored, attachment FROM items WHERE company_id=? ORDER BY id", (company_id,))
        rows = cur.fetchall()
        conn.close()

        self.items_table.blockSignals(True)
        self.items_table.setRowCount(len(rows) + 1)  # extra row for adding new
        for i, row in enumerate(rows):
            # id hidden
            id_item = QTableWidgetItem(str(row[0]))
            id_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.items_table.setItem(i, 0, id_item)

            name_it = QTableWidgetItem(row[1] or "")
            name_it.setFlags(name_it.flags() | Qt.ItemIsEditable)
            self.items_table.setItem(i, 1, name_it)

            issue_date = QTableWidgetItem(row[2] or "")
            issue_date.setFlags(issue_date.flags() | Qt.ItemIsEditable)
            self.items_table.setItem(i, 2, issue_date)

            review_date = QTableWidgetItem(row[3] or "")
            review_date.setFlags(review_date.flags() | Qt.ItemIsEditable)
            self.items_table.setItem(i, 3, review_date)

            status = QTableWidgetItem(row[4] or "")
            status.setFlags(status.flags() | Qt.ItemIsEditable)
            self.items_table.setItem(i, 4, status)

            perc = QTableWidgetItem(str(row[5]) if row[5] is not None else "")
            perc.setFlags(perc.flags() | Qt.ItemIsEditable)
            self.items_table.setItem(i, 5, perc)

            ignored = QTableWidgetItem("نعم" if row[6] else "لا")
            ignored.setFlags(ignored.flags() | Qt.ItemIsEditable)
            self.items_table.setItem(i, 6, ignored)

            attach_cell = QTableWidgetItem(os.path.basename(row[7]) if row[7] else "")
            attach_cell.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.items_table.setItem(i, 7, attach_cell)

            btn = QPushButton("فتح")
            btn.clicked.connect(partial(self.open_attachment_from_cell, row[7]))
            self.items_table.setCellWidget(i, 8, btn)

            # Color row based on review_date
            self._color_item_row(i, row[3], bool(row[6]))

        # last row for adding new item
        add_row = len(rows)
        self.items_table.setItem(add_row, 0, QTableWidgetItem(""))
        new_name = QTableWidgetItem("")
        new_name.setFlags(new_name.flags() | Qt.ItemIsEditable)
        self.items_table.setItem(add_row, 1, new_name)
        self.items_table.setItem(add_row, 2, QTableWidgetItem(QDate.currentDate().toString("yyyy-MM-dd")))
        self.items_table.setItem(add_row, 3, QTableWidgetItem(QDate.currentDate().addMonths(6).toString("yyyy-MM-dd")))
        self.items_table.setItem(add_row, 4, QTableWidgetItem(""))
        self.items_table.setItem(add_row, 5, QTableWidgetItem(""))
        self.items_table.setItem(add_row, 6, QTableWidgetItem("لا"))
        self.items_table.setItem(add_row, 7, QTableWidgetItem(""))
        btn_add = QPushButton("إضافة بند")
        btn_add.clicked.connect(self.add_item_from_row)
        self.items_table.setCellWidget(add_row, 8, btn_add)

        self.items_table.blockSignals(False)

    def _color_item_row(self, row_index, review_date_str, ignored):
        if not review_date_str or review_date_str.strip() == "":
            # if ignored flag, neutral; otherwise red
            color = QColor(255, 200, 200) if not ignored else QColor(230, 230, 230)
            # if ignored True -> grey
        else:
            try:
                rd = datetime.strptime(review_date_str, "%Y-%m-%d").date()
            except Exception:
                color = QColor(230, 230, 230)
            else:
                today = date.today()
                delta = (rd - today).days
                if delta < 0:
                    color = QColor(255, 170, 170)  # red-ish
                elif delta <= 30:
                    color = QColor(255, 255, 180)  # yellow-ish
                else:
                    color = QColor(255, 255, 255)
        # apply
        for c in range(self.items_table.columnCount()):
            cell = self.items_table.item(row_index, c)
            if cell:
                cell.setBackground(color)

    def add_item_from_row(self):
        # read last row
        r = self.items_table.rowCount() - 1
        name = self.items_table.item(r, 1).text().strip() if self.items_table.item(r, 1) else ""
        if not name:
            QMessageBox.warning(self, "خطأ", "أدخل اسم البند أولاً.")
            return
        issue = self.items_table.item(r, 2).text() if self.items_table.item(r, 2) else None
        review = self.items_table.item(r, 3).text() if self.items_table.item(r, 3) else None
        status = self.items_table.item(r, 4).text() if self.items_table.item(r, 4) else None
        try:
            perc = float(self.items_table.item(r, 5).text()) if self.items_table.item(r, 5) and self.items_table.item(r, 5).text().strip() else None
        except Exception:
            perc = None
        ignored = 1 if (self.items_table.item(r, 6) and self.items_table.item(r, 6).text().strip() == "نعم") else 0

        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("INSERT INTO items (company_id, item_name, issue_date, review_date, status, evaluation_percent, ignored) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (self.current_company_id, name, issue, review, status, perc, ignored))
        conn.commit()
        conn.close()
        self.load_items(self.current_company_id)
        self.trigger_auto_backup()

    def on_item_cell_changed(self, item: QTableWidgetItem):
        # only handle if row has ID
        row = item.row()
        id_item_widget = self.items_table.item(row, 0)
        if id_item_widget and id_item_widget.text().strip():
            try:
                item_id = int(id_item_widget.text())
            except Exception:
                return
            # map column to field
            col = item.column()
            field_map = {1: "item_name", 2: "issue_date", 3: "review_date", 4: "status", 5: "evaluation_percent", 6: "ignored"}
            if col not in field_map:
                return
            field = field_map[col]
            value = item.text().strip()
            if field == "ignored":
                val = 1 if value == "نعم" else 0
            else:
                val = value
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute(f"UPDATE items SET {field}=? WHERE id=?", (val, item_id))
            conn.commit()
            conn.close()
            # recolor
            review_date = self.items_table.item(row, 3).text() if self.items_table.item(row, 3) else None
            ignored_flag = True if (self.items_table.item(row, 6) and self.items_table.item(row, 6).text().strip() == "نعم") else False
            self._color_item_row(row, review_date, ignored_flag)
            # trigger backup debounce
            self.trigger_auto_backup()
        else:
            # new rows are handled by add button
            pass

    # ----------------------- Attachments -----------------------
    def open_attachment_from_cell(self, path):
        if not path:
            QMessageBox.information(self, "لا يوجد مرفق", "لايوجد مرفق لهذا البند.")
            return
        if not os.path.exists(path):
            QMessageBox.warning(self, "غير موجود", f"المرفق غير موجود في المسار:\n{path}")
            return
        try:
            if sys.platform.startswith('darwin'):
                os.system(f"open \"{path}\"")
            elif os.name == 'nt':
                os.startfile(path)
            else:
                os.system(f"xdg-open \"{path}\"")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"تعذر فتح الملف:\n{e}")

    def attach_file_to_selected_item(self):
        row = self.items_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "خطأ", "اختر بندًا أولاً.")
            return
        id_item_widget = self.items_table.item(row, 0)
        if not id_item_widget or not id_item_widget.text().strip():
            QMessageBox.warning(self, "خطأ", "اختر بندًا محفوظًا (غير جديد).")
            return
        item_id = int(id_item_widget.text())
        file_path, _ = QFileDialog.getOpenFileName(self, "اختر المرفق")
        if not file_path:
            return
        # copy to attachments/<company_name>/
        safe_name = sanitize_filename(self.current_company_name)
        dest_dir = os.path.join(self.base_folder, 'attachments', safe_name)
        os.makedirs(dest_dir, exist_ok=True)
        dest_file = os.path.join(dest_dir, os.path.basename(file_path))
        try:
            shutil.copy(file_path, dest_file)
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل نسخ الملف: {e}")
            return
        # save path in DB
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("UPDATE items SET attachment=? WHERE id=?", (dest_file, item_id))
        conn.commit()
        conn.close()
        # update UI
        self.items_table.item(row, 7).setText(os.path.basename(dest_file))
        btn = self.items_table.cellWidget(row, 8)
        if btn:
            btn.clicked.disconnect()
            btn.clicked.connect(partial(self.open_attachment_from_cell, dest_file))
        self.trigger_auto_backup()

    # ----------------------- Exports & Backups -----------------------
    def export_selected_company(self):
        if pd is None:
            QMessageBox.warning(self, "مفقود", "المكتبة pandas مطلوبة لتصدير Excel. قم بتثبيتها: pip install pandas openpyxl")
            return
        sel = self.companies_table.currentRow()
        if sel < 0:
            QMessageBox.warning(self, "خطأ", "اختر شركة أولا.")
            return
        cid = int(self.companies_table.item(sel, 0).text())
        conn = sqlite3.connect(DB_FILE)
        df_company = pd.read_sql_query("SELECT * FROM companies WHERE id=?", conn, params=(cid,))
        df_items = pd.read_sql_query("SELECT * FROM items WHERE company_id=?", conn, params=(cid,))
        df_insp = pd.read_sql_query("SELECT * FROM inspections WHERE company_id=?", conn, params=(cid,))
        conn.close()

        save_path, _ = QFileDialog.getSaveFileName(self, "احفظ ملف Excel", f"{self.current_company_name}.xlsx", "Excel Files (*.xlsx)")
        if not save_path:
            return
        try:
            with pd.ExcelWriter(save_path) as writer:
                df_company.to_excel(writer, sheet_name='Company', index=False)
                df_items.to_excel(writer, sheet_name='Items', index=False)
                df_insp.to_excel(writer, sheet_name='Inspections', index=False)
            QMessageBox.information(self, "تم", f"تم حفظ ملف Excel في:\n{save_path}")
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل التصدير: {e}")

    def manual_backup(self):
        # create backup folder per company
        sel = self.companies_table.currentRow()
        if sel < 0:
            QMessageBox.warning(self, "خطأ", "اختر شركة أولاً")
            return
        cid = int(self.companies_table.item(sel, 0).text())
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT name FROM companies WHERE id=?", (cid,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return
        cname = row[0]
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        backup_dir = os.path.join(self.base_folder, 'backup', f"{sanitize_filename(cname)}_{timestamp}")
        os.makedirs(backup_dir, exist_ok=True)

        # export to excel
        if pd is None:
            QMessageBox.warning(self, "مفقود", "المكتبة pandas مطلوبة للتصدير. تثبتها ثم حاول مرة اخرى.")
            return
        conn = sqlite3.connect(DB_FILE)
        df_items = pd.read_sql_query("SELECT * FROM items WHERE company_id=?", conn, params=(cid,))
        df_insp = pd.read_sql_query("SELECT * FROM inspections WHERE company_id=?", conn, params=(cid,))
        conn.close()
        try:
            with pd.ExcelWriter(os.path.join(backup_dir, 'company_data.xlsx')) as writer:
                df_items.to_excel(writer, sheet_name='Items', index=False)
                df_insp.to_excel(writer, sheet_name='Inspections', index=False)
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل إنشاء Excel: {e}")
            return

        # copy attachments folder for company
        attachments_src = os.path.join(self.base_folder, 'attachments', sanitize_filename(cname))
        if os.path.exists(attachments_src):
            try:
                shutil.copytree(attachments_src, os.path.join(backup_dir, 'attachments'))
            except Exception as e:
                print('copy attachments failed', e)

        # summary
        summary_text = f"اسم الشركة: {cname}\nتاريخ النسخ: {timestamp}\n"
        with open(os.path.join(backup_dir, 'summary.txt'), 'w', encoding='utf-8') as f:
            f.write(summary_text)

        QMessageBox.information(self, "تم", f"تم إنشاء النسخة الاحتياطية في:\n{backup_dir}")

    def trigger_auto_backup(self):
        # start/restart debounce timer
        self._backup_timer.start(AUTO_BACKUP_AFTER_EDIT_SECONDS * 1000)

    def _perform_auto_backup(self):
        if not self.base_folder:
            return
        auto_backup_db(self.base_folder)

    # ----------------------- Utilities -----------------------
    def change_base_folder(self):
        self.select_base_folder(first_time=False)
        QMessageBox.information(self, "تم", f"تم تغيير المجلد الرئيسي إلى:\n{self.base_folder}")


# ----------------------- Helpers -----------------------

def sanitize_filename(name: str) -> str:
    # simple sanitize to create folder names
    keep = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_ ";
    return ''.join(c for c in name if c in keep).strip().replace(' ', '_')


# ----------------------- Main -----------------------

def main():
    app = QApplication(sys.argv)
    win = CompanyManager()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
