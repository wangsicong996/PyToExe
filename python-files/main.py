import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import threading
import os
import time
from typing import Dict, List, Optional
import json

# Tuo omat moduulit
from scanner import LocalScanner
from openai_agent import OpenAIAgent
from ext_scanner import ExternalScannerManager
from storage_manager import StorageManager
from learning_engine import LearningEngine
from rate_limiter import api_rate_limiter
from config import Config

class AegisAntivirusGUI:
    """Aegis AI Antivirus -pääsovellus"""
    
    def __init__(self):
        # Alusta customtkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Luo pääikkuna
        self.root = ctk.CTk()
        self.root.title(Config.APP_NAME)
        self.root.geometry(f"{Config.WINDOW_WIDTH}x{Config.WINDOW_HEIGHT}")
        self.root.minsize(800, 600)
        
        # Alusta komponentit
        self.local_scanner = LocalScanner()
        self.openai_agent = None
        self.ext_scanner_manager = ExternalScannerManager()
        self.storage_manager = StorageManager()
        self.learning_engine = LearningEngine(self.storage_manager)
        
        # Alusta OpenAI-agentti
        try:
            self.openai_agent = OpenAIAgent()
        except Exception as e:
            print(f"OpenAI-agentti ei voitu alustaa: {e}")
        
        # GUI-komponentit
        self.current_scan_result = None
        self.scanning = False
        
        self.setup_ui()
        # Näytä placeholder ja päivitä API-tila taustalla, jotta UI ei blokkaudu
        try:
            self.api_status_text.delete("1.0", "end")
            self.api_status_text.insert("1.0", "Tarkistetaan API-tila...")
        except Exception:
            pass
        self.root.after(200, lambda: threading.Thread(target=self.update_api_status, daemon=True).start())
        
        # Käynnistä siivous taustalla
        self.cleanup_old_data()
    
    def setup_ui(self):
        """Aseta käyttöliittymä"""
        
        # Pääkehys
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Otsikko
        self.title_frame = ctk.CTkFrame(self.main_frame)
        self.title_frame.pack(fill="x", pady=(0, 10))
        
        self.title_label = ctk.CTkLabel(
            self.title_frame,
            text=Config.APP_NAME,
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=20)
        
        # Sisältökehys (kaksi saraketta)
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(fill="both", expand=True)
        
        # Vasen paneeli - Toiminnot
        self.left_panel = ctk.CTkFrame(self.content_frame)
        self.left_panel.pack(side="left", fill="y", padx=(10, 5), pady=10)
        self.left_panel.configure(width=300)
        
        # Toiminnot-otsikko
        self.actions_title = ctk.CTkLabel(
            self.left_panel,
            text="Toiminnot",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.actions_title.pack(pady=(20, 10))
        
        # Skannausnapit
        self.scan_file_btn = ctk.CTkButton(
            self.left_panel,
            text="Skannaa tiedosto",
            command=self.scan_file,
            height=50,
            font=ctk.CTkFont(size=14)
        )
        self.scan_file_btn.pack(pady=10, padx=20, fill="x")
        
        self.scan_folder_btn = ctk.CTkButton(
            self.left_panel,
            text="Skannaa kansio",
            command=self.scan_folder,
            height=50,
            font=ctk.CTkFont(size=14)
        )
        self.scan_folder_btn.pack(pady=10, padx=20, fill="x")
        
        self.scan_drive_btn = ctk.CTkButton(
            self.left_panel,
            text="Skannaa levy",
            command=self.scan_drive,
            height=50,
            font=ctk.CTkFont(size=14)
        )
        self.scan_drive_btn.pack(pady=10, padx=20, fill="x")
        
        # API-tila
        self.api_status_frame = ctk.CTkFrame(self.left_panel)
        self.api_status_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        self.api_status_title = ctk.CTkLabel(
            self.api_status_frame,
            text="API-tila:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.api_status_title.pack(pady=(15, 5))
        
        self.api_status_text = ctk.CTkTextbox(
            self.api_status_frame,
            height=100,
            font=ctk.CTkFont(size=12)
        )
        self.api_status_text.pack(pady=(0, 15), padx=15, fill="x")
        
        # Oikea paneeli - Tulokset
        self.right_panel = ctk.CTkFrame(self.content_frame)
        self.right_panel.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)
        
        # Tulokset-otsikko
        self.results_title = ctk.CTkLabel(
            self.right_panel,
            text="Skannauksen tulokset",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.results_title.pack(pady=(20, 10))
        
        # Tulosten tekstikenttä
        self.results_text = ctk.CTkTextbox(
            self.right_panel,
            font=ctk.CTkFont(size=12)
        )
        self.results_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Palaute-napit
        self.feedback_frame = ctk.CTkFrame(self.right_panel)
        self.feedback_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.false_positive_btn = ctk.CTkButton(
            self.feedback_frame,
            text="Väärä positiivinen",
            command=self.report_false_positive,
            height=40,
            fg_color="orange"
        )
        self.false_positive_btn.pack(side="left", padx=(20, 10), pady=15)
        
        self.false_negative_btn = ctk.CTkButton(
            self.feedback_frame,
            text="Väärä negatiivinen",
            command=self.report_false_negative,
            height=40,
            fg_color="red"
        )
        self.false_negative_btn.pack(side="right", padx=(10, 20), pady=15)
        
        # Tilarivi
        self.status_frame = ctk.CTkFrame(self.main_frame)
        self.status_frame.pack(fill="x", pady=(10, 0))
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Valmis",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=10)
        
        # Edistymispalkki (piilotettu aluksi)
        self.progress_frame = ctk.CTkFrame(self.main_frame)
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
    
    def update_api_status(self):
        """Päivitä API-tilatiedot"""
        status_text = ""
        
        # OpenAI
        if self.openai_agent and self.openai_agent.is_api_available():
            status_text += "✓ OpenAI\n"
        else:
            status_text += "✗ OpenAI\n"
        
        # VirusTotal
        if self.ext_scanner_manager.scanners['virustotal'].is_available():
            status_text += "✓ VirusTotal\n"
        else:
            status_text += "✗ VirusTotal\n"
        
        # Hybrid Analysis
        if self.ext_scanner_manager.scanners['hybrid_analysis'].is_available():
            status_text += "✓ Hybrid Analysis\n"
        else:
            status_text += "✗ Hybrid Analysis\n"
        
        status_text += "\nVirusTotal & Hybrid Analysis ovat ILMAISIA!"
        
        # Lisää rate limit tilastot
        rate_stats = api_rate_limiter.get_all_stats()
        status_text += f"\n\nRate Limit tilastot:"
        status_text += f"\nGlobaalit pyynnot/min: {rate_stats['global']['requests_last_minute']}"
        status_text += f"\nGlobaalit pyynnot/h: {rate_stats['global']['requests_last_hour']}"
        
        for service, stats in rate_stats['services'].items():
            status_text += f"\n{service}: {stats['requests_last_minute']}/min"
        
        # Päivitä GUI pääsäikeessä
        self.root.after(0, lambda: self._update_api_status_ui(status_text))
    
    def _update_api_status_ui(self, status_text: str):
        """Päivitä API-tila UI:ssa pääsäikeessä"""
        self.api_status_text.delete("1.0", "end")
        self.api_status_text.insert("1.0", status_text)
    
    def scan_file(self):
        """Skannaa yksittäinen tiedosto"""
        if self.scanning:
            messagebox.showwarning("Varoitus", "Skannaus on jo käynnissä!")
            return
        
        file_path = filedialog.askopenfilename(
            title="Valitse skannattava tiedosto",
            filetypes=[("Kaikki tiedostot", "*.*")]
        )
        
        if file_path:
            self.start_scan("file", file_path)
    
    def scan_folder(self):
        """Skannaa kansio"""
        if self.scanning:
            messagebox.showwarning("Varoitus", "Skannaus on jo käynnissä!")
            return
        
        folder_path = filedialog.askdirectory(title="Valitse skannattava kansio")
        
        if folder_path:
            self.start_scan("folder", folder_path)
    
    def scan_drive(self):
        """Skannaa levy"""
        if self.scanning:
            messagebox.showwarning("Varoitus", "Skannaus on jo käynnissä!")
            return
        
        # Hae käytettävissä olevat levyt
        drives = []
        for drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            if os.path.exists(f"{drive}:"):
                drives.append(f"{drive}:")
        
        if not drives:
            messagebox.showerror("Virhe", "Ei löytynyt levyjä skannattavaksi!")
            return
        
        # Kysy levy
        drive = simpledialog.askstring(
            "Valitse levy",
            f"Syötä levyn kirjain (käytettävissä: {', '.join(drives)}):"
        )
        
        if drive and f"{drive.upper()}:" in drives:
            self.start_scan("drive", f"{drive.upper()}:")
        elif drive:
            messagebox.showerror("Virhe", "Virheellinen levy!")
    
    def start_scan(self, scan_type: str, path: str):
        """Käynnistä skannaus taustalla"""
        self.scanning = True
        self.update_ui_for_scanning(True)
        
        # Käynnistä skannaus uudessa säikeessä
        scan_thread = threading.Thread(
            target=self.perform_scan,
            args=(scan_type, path),
            daemon=True
        )
        scan_thread.start()
    
    def perform_scan(self, scan_type: str, path: str):
        """Suorita skannaus"""
        try:
            self.update_status("Skannaus käynnissä...")
            
            # 1. Paikallinen skannaus
            self.update_progress(0.1, "Paikallinen heuristiikka...")
            if scan_type == "file":
                local_result = self.local_scanner.scan_file(path)
            elif scan_type == "folder":
                local_result = self.local_scanner.scan_directory(path)
            elif scan_type == "drive":
                local_result = self.local_scanner.scan_drive(path)
            else:
                raise ValueError("Tuntematon skannaustyyppi")
            
            if local_result.get('status') != 'success':
                self.show_error("Paikallinen skannaus epäonnistui", local_result.get('message', 'Tuntematon virhe'))
                return
            
            # 2. OpenAI-analyysi
            openai_result = None
            if self.openai_agent:
                self.update_progress(0.3, "OpenAI-analyysi...")
                if scan_type == "file":
                    openai_result = self.openai_agent.analyze_file_metadata(local_result)
                else:
                    # Kansio/levy - analysoi vain epäilyttävät tiedostot
                    suspicious_files = [f for f in local_result.get('scanned_files', []) 
                                      if f.get('risk_level') in ['MEDIUM', 'HIGH']]
                    if suspicious_files:
                        openai_result = self.openai_agent.analyze_multiple_files(suspicious_files)
            
            # 3. Tarkista tarvitaanko ulkoista skannausta
            needs_external = False
            if openai_result and openai_result.get('status') == 'success':
                recommendation = self.openai_agent.get_scan_recommendation(local_result, openai_result)
                needs_external = recommendation.get('needs_external_scan', False)
            else:
                # Jos OpenAI ei ole saatavilla, käytä paikallista riskiä
                risk_level = local_result.get('risk_level', 'UNKNOWN')
                if risk_level in ['MEDIUM', 'HIGH']:
                    needs_external = True
            
            # 4. Ulkoinen skannaus tarvittaessa
            external_result = None
            if needs_external:
                self.update_progress(0.5, "Ulkoinen skannaus...")
                
                # Kysy käyttäjän suostumus
                if not self.ask_external_scan_permission(local_result):
                    self.update_progress(0.8, "Ulkoinen skannaus hylätty...")
                else:
                    # Hae tiedoston hash
                    file_hash = local_result.get('sha256', '')
                    if file_hash:
                        external_result = self.ext_scanner_manager.scan_file(file_hash, path)
            
            # 5. Yhdistä tulokset
            self.update_progress(0.8, "Yhdistetään tulokset...")
            combined_result = self.combine_scan_results(local_result, openai_result, external_result)
            
            # 6. Tallenna tulokset
            self.storage_manager.add_scan_to_history(combined_result)
            self.current_scan_result = combined_result
            
            # 7. Näytä tulokset
            self.update_progress(1.0, "Valmis!")
            self.root.after(0, lambda: self.display_results(combined_result))
            
        except Exception as e:
            self.root.after(0, lambda: self.show_error("Skannaus epäonnistui", str(e)))
        finally:
            self.scanning = False
            self.root.after(0, lambda: self.update_ui_for_scanning(False))
    
    def ask_external_scan_permission(self, local_result: Dict) -> bool:
        """Kysy käyttäjän suostumus ulkoiseen skannaukseen"""
        file_name = local_result.get('file_name', 'Tuntematon tiedosto')
        file_size = local_result.get('file_size', 0)
        risk_level = local_result.get('risk_level', 'UNKNOWN')
        
        message = f"""
Tiedosto: {file_name}
Koko: {file_size / 1024 / 1024:.1f} MB
Paikallinen riskitaso: {risk_level}

Haluatko lähettää tiedoston ulkoisiin skannauspalveluihin varmennusta varten?

✓ VirusTotal (hash-haku ensin, sitten tiedoston lataus)
✓ Hybrid Analysis (käyttäytymisanalyysi)

Tiedot lähetetään turvallisesti ja käytetään vain skannaukseen.
"""
        
        result = messagebox.askyesno("Ulkoinen skannaus", message)
        return result
    
    def combine_scan_results(self, local_result: Dict, openai_result: Dict = None, external_result: Dict = None) -> Dict:
        """Yhdistä kaikkien skannauspalveluiden tulokset"""
        
        combined = {
            'scan_id': f"scan_{int(time.time())}",
            'scan_time': time.time(),
            'scan_date': time.strftime("%Y-%m-%d %H:%M:%S"),
            'local_result': local_result,
            'openai_result': openai_result,
            'external_result': external_result
        }
        
        # Määritä lopullinen riskitaso
        risk_levels = [local_result.get('risk_level', 'UNKNOWN')]
        
        if openai_result and openai_result.get('status') == 'success':
            risk_levels.append(openai_result.get('risk_level', 'UNKNOWN'))
        
        if external_result and external_result.get('status') == 'success':
            combined_verdict = self.ext_scanner_manager.get_combined_verdict(external_result.get('results', {}))
            if combined_verdict.get('status') == 'success':
                risk_levels.append(combined_verdict.get('combined_risk_level', 'UNKNOWN'))
        
        # Määritä korkein riskitaso
        risk_priority = {'CRITICAL': 5, 'HIGH': 4, 'MEDIUM': 3, 'LOW': 2, 'CLEAN': 1, 'UNKNOWN': 0}
        final_risk = max(risk_levels, key=lambda x: risk_priority.get(x, 0))
        
        combined['final_risk_level'] = final_risk
        combined['status'] = 'success'
        
        return combined
    
    def display_results(self, result: Dict):
        """Näytä skannauksen tulokset"""
        
        results_text = f"=== SKANNAUKSEN TULOKSET ===\n"
        results_text += f"Skannausaika: {result.get('scan_date', 'Tuntematon')}\n"
        results_text += f"Lopullinen riskitaso: {result.get('final_risk_level', 'UNKNOWN')}\n\n"
        
        # Paikallinen skannaus
        local_result = result.get('local_result', {})
        if local_result:
            results_text += "--- PAIKALLINEN HEURISTIIKKA ---\n"
            results_text += f"Tiedosto: {local_result.get('file_name', 'Tuntematon')}\n"
            results_text += f"Koko: {local_result.get('file_size', 0) / 1024 / 1024:.1f} MB\n"
            results_text += f"Riskitaso: {local_result.get('risk_level', 'UNKNOWN')}\n"
            results_text += f"SHA256: {local_result.get('sha256', 'Tuntematon')[:16]}...\n"
            
            risk_factors = local_result.get('risk_factors', [])
            if risk_factors:
                results_text += f"Riskitekijät: {', '.join(risk_factors)}\n"
            results_text += "\n"
        
        # OpenAI-analyysi
        openai_result = result.get('openai_result', {})
        if openai_result and openai_result.get('status') == 'success':
            results_text += "--- OPENAI ANALYYSI ---\n"
            results_text += f"Riskitaso: {openai_result.get('risk_level', 'UNKNOWN')}\n"
            results_text += f"Luottamus: {openai_result.get('confidence', 0):.2f}\n"
            
            reasoning = openai_result.get('reasoning', '')
            if reasoning:
                results_text += f"Perustelu: {reasoning}\n"
            
            recommendations = openai_result.get('recommendations', '')
            if recommendations:
                results_text += f"Suositukset: {recommendations}\n"
            results_text += "\n"
        
        # Ulkoinen skannaus
        external_result = result.get('external_result', {})
        if external_result and external_result.get('status') == 'success':
            results_text += "--- ULKOINEN SKANNAUS ---\n"
            
            scanner_results = external_result.get('results', {})
            for scanner_name, scanner_result in scanner_results.items():
                if scanner_result.get('status') == 'success':
                    results_text += f"{scanner_name.upper()}:\n"
                    results_text += f"  Riskitaso: {scanner_result.get('risk_level', 'UNKNOWN')}\n"
                    
                    if scanner_name == 'virustotal':
                        malicious = scanner_result.get('malicious_count', 0)
                        total = scanner_result.get('total_engines', 0)
                        results_text += f"  Malicious: {malicious}/{total}\n"
                    elif scanner_name == 'hybrid_analysis':
                        threat_score = scanner_result.get('threat_score', 0)
                        results_text += f"  Threat Score: {threat_score}/100\n"
            results_text += "\n"
        
        # Yhteenveto
        results_text += "=== YHTEENVETO ===\n"
        final_risk = result.get('final_risk_level', 'UNKNOWN')
        
        if final_risk in ['HIGH', 'CRITICAL']:
            results_text += "⚠️ KORKEA RISKI - Suositellaan tiedoston poistamista!\n"
        elif final_risk == 'MEDIUM':
            results_text += "⚠️ KESKIMÄÄRÄINEN RISKI - Varoituksella käytettävä\n"
        elif final_risk == 'LOW':
            results_text += "ℹ️ MATALA RISKI - Normaali käyttö OK\n"
        else:
            results_text += "✅ PUHTAAS - Tiedosto näyttää turvalliselta\n"
        
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", results_text)
        
        self.update_status("Skannaus valmis")
    
    def report_false_positive(self):
        """Raportoi väärä positiivinen"""
        if not self.current_scan_result:
            messagebox.showwarning("Varoitus", "Ei skannauksen tuloksia raportoitavaksi!")
            return
        
        comment = simpledialog.askstring(
            "Väärä positiivinen",
            "Lisää kommentti (valinnainen):"
        )
        
        self.learning_engine.process_user_feedback(
            self.current_scan_result,
            'false_positive',
            comment or ""
        )
        
        messagebox.showinfo("Kiitos", "Palaute tallennettu! Se auttaa parantamaan skannauksen tarkkuutta.")
    
    def report_false_negative(self):
        """Raportoi väärä negatiivinen"""
        if not self.current_scan_result:
            messagebox.showwarning("Varoitus", "Ei skannauksen tuloksia raportoitavaksi!")
            return
        
        comment = simpledialog.askstring(
            "Väärä negatiivinen",
            "Lisää kommentti (valinnainen):"
        )
        
        self.learning_engine.process_user_feedback(
            self.current_scan_result,
            'false_negative',
            comment or ""
        )
        
        messagebox.showinfo("Kiitos", "Palaute tallennettu! Se auttaa parantamaan skannauksen tarkkuutta.")
    
    def update_status(self, message: str):
        """Päivitä tilarivi"""
        self.root.after(0, lambda: self.status_label.configure(text=message))
    
    def update_progress(self, value: float, message: str):
        """Päivitä edistymispalkki"""
        self.root.after(0, lambda: self._update_progress_ui(value, message))
    
    def _update_progress_ui(self, value: float, message: str):
        """Päivitä edistymispalkki UI:ssa"""
        if not hasattr(self, 'progress_shown'):
            self.progress_frame.pack(fill="x", pady=(0, 10))
            self.progress_bar.pack(pady=(10, 5), padx=20, fill="x")
            self.progress_label.pack(pady=(0, 10))
            self.progress_shown = True
        
        self.progress_bar.set(value)
        self.progress_label.configure(text=message)
        
        if value >= 1.0:
            self.root.after(2000, self.hide_progress)
    
    def hide_progress(self):
        """Piilota edistymispalkki"""
        if hasattr(self, 'progress_shown'):
            self.progress_frame.pack_forget()
            self.progress_shown = False
    
    def update_ui_for_scanning(self, scanning: bool):
        """Päivitä UI skannauksen tilan mukaan"""
        state = "disabled" if scanning else "normal"
        
        self.scan_file_btn.configure(state=state)
        self.scan_folder_btn.configure(state=state)
        self.scan_drive_btn.configure(state=state)
        
        if not scanning:
            self.update_status("Valmis")
    
    def show_error(self, title: str, message: str):
        """Näytä virheilmoitus"""
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", f"VIRHE: {title}\n\n{message}")
        self.update_status("Virhe")
        messagebox.showerror(title, message)
    
    def cleanup_old_data(self):
        """Siivoa vanhat datat taustalla"""
        def cleanup():
            try:
                self.storage_manager.cleanup_old_data(days_to_keep=30)
            except Exception as e:
                print(f"Siivous epäonnistui: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup, daemon=True)
        cleanup_thread.start()
    
    def run(self):
        """Käynnistä sovellus"""
        self.root.mainloop()

def main_app():
    """Pääfunktio"""
    try:
        app = AegisAntivirusGUI()
        app.run()
    except Exception as e:
        print(f"Sovelluksen käynnistys epäonnistui: {e}")
        messagebox.showerror("Virhe", f"Sovelluksen käynnistys epäonnistui:\n{e}")

if __name__ == "__main__":
    main_app()
