#!/usr/bin/env python3
"""
Excel Search GUI (نسخة محسّنة)
- واجهة احترافية حديثة بألوان أنيقة
- البحث في جميع ملفات Excel داخل مجلد والمجلدات الفرعية
- عرض النتائج في جدول تفاعلي
- النقر المزدوج على نتيجة يفتح الملف مباشرة في Excel على الورقة والصف المقابل
- إمكانية التحكم في حجم الخط للواجهة وحفظ الإعداد
"""

import os
import sys
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import json

SUPPORTED_EXT = ('.xlsx', '.xls')
CONFIG_FILE = 'config.json'

class ExcelSearcher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('🔍 البحث في ملفات Excel — Excel Smart Finder')
        self.geometry('1100x650')
        self.configure(bg='#f4f6f8')

        # تحميل إعدادات الخط
        self.font_size = self.load_font_size()
        self.default_font = ('Segoe UI', self.font_size)
        self.option_add('*Font', self.default_font)

        self._build_ui()
        self.results = []

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#f4f6f8', font=self.default_font)
        style.configure('TLabel', background='#f4f6f8', font=self.default_font)
        style.configure('TButton', font=(self.default_font[0], self.default_font[1], 'bold'), padding=5)
        style.configure('Treeview.Heading', font=(self.default_font[0], self.default_font[1], 'bold'))

        # === الشريط العلوي ===
        frm_top = ttk.Frame(self)
        frm_top.pack(fill='x', padx=15, pady=10)

        ttk.Label(frm_top, text='📁 مجلد الملفات:').grid(row=0, column=0, sticky='w')
        self.var_folder = tk.StringVar()
        ent_folder = ttk.Entry(frm_top, textvariable=self.var_folder, width=70)
        ent_folder.grid(row=0, column=1, padx=6)
        ttk.Button(frm_top, text='استعراض...', command=self.browse_folder).grid(row=0, column=2)

        ttk.Label(frm_top, text='🔎 البحث (جزئي):').grid(row=1, column=0, sticky='w', pady=6)
        self.var_query = tk.StringVar()
        ent_query = ttk.Entry(frm_top, textvariable=self.var_query, width=50)
        ent_query.grid(row=1, column=1, sticky='w')
        ent_query.bind('<Return>', lambda e: self.start_search())

        ttk.Button(frm_top, text='بدء البحث', command=self.start_search).grid(row=1, column=2, sticky='w')

        self.var_ext = tk.BooleanVar(value=True)
        ttk.Checkbutton(frm_top, text='يشمل المجلدات الفرعية', variable=self.var_ext).grid(row=2, column=1, sticky='w')

        # === ضبط حجم الخط ===
        frm_font = ttk.Frame(frm_top)
        frm_font.grid(row=3, column=0, columnspan=3, pady=6, sticky='w')
        ttk.Label(frm_font, text='حجم الخط:').pack(side='left')
        self.var_font = tk.IntVar(value=self.font_size)
        spn_font = ttk.Spinbox(frm_font, from_=8, to=24, textvariable=self.var_font, width=5)
        spn_font.pack(side='left', padx=5)
        ttk.Button(frm_font, text='تطبيق', command=self.apply_font_size).pack(side='left')

        # === شريط الحالة ===
        self.status = ttk.Label(self, text='جاهز', anchor='w', relief='sunken', padding=4)
        self.status.pack(fill='x', padx=10, pady=(0,6))

        # === جدول النتائج ===
        cols = ('file', 'sheet', 'row', 'matched_cols', 'row_data')
        self.tree = ttk.Treeview(self, columns=cols, show='headings')
        self.tree.heading('file', text='اسم الملف')
        self.tree.heading('sheet', text='اسم الورقة')
        self.tree.heading('row', text='رقم الصف')
        self.tree.heading('matched_cols', text='الأعمدة المطابقة')
        self.tree.heading('row_data', text='بيانات الصف')

        self.tree.column('file', width=220)
        self.tree.column('sheet', width=130)
        self.tree.column('row', width=80, anchor='center')
        self.tree.column('matched_cols', width=180)
        self.tree.column('row_data', width=460)

        vsb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        self.tree.pack(side='left', fill='both', expand=True, padx=(15,0), pady=10)
        vsb.pack(side='right', fill='y', pady=10)

        # === الشريط السفلي ===
        frm_bottom = ttk.Frame(self)
        frm_bottom.pack(fill='x', padx=15, pady=10)
        ttk.Button(frm_bottom, text='💾 تصدير النتائج إلى Excel', command=self.export_results).pack(side='left')
        ttk.Button(frm_bottom, text='🧹 مسح النتائج', command=self.clear_results).pack(side='left', padx=8)
        ttk.Label(frm_bottom, text='انقر مرتين على الصف لفتح الملف في Excel').pack(side='right')

        # حدث النقر المزدوج
        self.tree.bind('<Double-1>', self.on_double_click_row)

    def apply_font_size(self):
        self.font_size = self.var_font.get()
        self.default_font = ('Segoe UI', self.font_size)
        self.option_add('*Font', self.default_font)
        self.save_font_size()

    def save_font_size(self):
        config = {'font_size': self.font_size}
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f)

    def load_font_size(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('font_size', 10)
            except:
                return 10
        return 10

    # باقي الدوال مثل start_search, browse_folder, export_results, clear_results, on_double_click_row تبقى كما هي
    ...
