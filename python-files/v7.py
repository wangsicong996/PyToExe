import customtkinter
from tkinter import messagebox
import requests
from bs4 import BeautifulSoup
from threading import Thread
import re
import time
import webbrowser
import json
import os
from mistralai import Mistral # --- MODIFIÉ --- Importation correcte

# --- Thème et apparence ---
customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("dark-blue")

# --- Fonctions d'extraction de données ---
# ... (Le reste des fonctions d'extraction comme parse_and_explain_vector, get_nvd_data, etc. restent inchangées)
CVSS_V3_METRICS_EXPLANATIONS = {
    'AV': {'name': "Vecteur d'attaque", 'values': {'N': "Réseau (N)", 'A': "Adjacent (A)", 'L': "Local (L)", 'P': "Physique (P)"}},
    'AC': {'name': "Complexité", 'values': {'L': "Basse (L)", 'H': "Élevée (H)"}},
    'PR': {'name': "Privilèges requis", 'values': {'N': "Aucun (N)", 'L': "Bas (L)", 'H': "Élevés (H)"}},
    'UI': {'name': "Interaction utilisateur", 'values': {'N': "Aucune (N)", 'R': "Requise (R)"}},
    'S': {'name': "Portée (Scope)", 'values': {'U': "Inchangée (U)", 'C': "Changée (C)"}},
    'C': {'name': "Confidentialité", 'values': {'N': "Aucune (N)", 'L': "Basse (L)", 'H': "Élevée (H)"}},
    'I': {'name': "Intégrité", 'values': {'N': "Aucune (N)", 'L': "Basse (L)", 'H': "Élevée (H)"}},
    'A': {'name': "Disponibilité", 'values': {'N': "Aucune (N)", 'L': "Basse (L)", 'H': "Élevée (H)"}}
}
def parse_and_explain_vector(vector_string):
    if not vector_string: return ""
    explanation_lines = ["🔑 Détails des métriques :"]
    try: clean_vector = vector_string.split('/', 1)[1]
    except IndexError: clean_vector = vector_string
    metrics = clean_vector.split('/')
    for metric in metrics:
        try:
            key, value = metric.split(':')
            if key in CVSS_V3_METRICS_EXPLANATIONS:
                name = CVSS_V3_METRICS_EXPLANATIONS[key]['name']
                desc = CVSS_V3_METRICS_EXPLANATIONS[key]['values'].get(value, "Inconnue")
                explanation_lines.append(f"  • {name:<22} : {desc}")
        except ValueError: continue
    return "\n".join(explanation_lines)
def get_nvd_data(cve_id):
    base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    params = {'cveId': cve_id.upper()}
    try:
        time.sleep(0.6)
        response = requests.get(base_url, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
        if data['totalResults'] == 0: return {'error': "CVE non trouvée sur le NVD."}
        vuln = data['vulnerabilities'][0]['cve']
        result = {'references': vuln.get('references', [])}
        if 'cvssMetricV31' in vuln['metrics']:
            metric = vuln['metrics']['cvssMetricV31'][0]['cvssData']
            result.update({'version': "CVSS v3.1", 'score': metric.get('baseScore'), 'severite': metric.get('baseSeverity'), 'vecteur': metric.get('vectorString')})
        else: result['error_score'] = "Aucun score CVSS v3.x trouvé."
        return result
    except requests.exceptions.RequestException as e: return {'error': f"Erreur de connexion NVD : {e}"}
    except (KeyError, IndexError) as e: return {'error': f"Réponse JSON inattendue du NVD : {e}"}
def get_suse_score(cve_id):
    url = f"https://www.suse.com/security/cve/{cve_id.upper()}.html"
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", class_="table")
        if not table: return {"error": "Tableau CVSS introuvable."}
        rows = table.find_all("tr")
        if len(rows) < 3: return {"error": "Tableau CVSS SUSE incomplet."}
        base_score_cell = rows[1].find_all("td")[1].get_text(strip=True)
        vector_cell = rows[2].find_all("td")[1].get_text(strip=True)
        if "CVSS:" in vector_cell:
            version_part = vector_cell.split("CVSS:")[1].split('/')[0]
            vector = "/".join(vector_cell.split("CVSS:")[1].split('/')[1:])
            version = version_part
        else: return {"error": "Vecteur CVSS SUSE non trouvé."}
        return {f"v{version}": {"score": base_score_cell, "vector": vector}}
    except requests.exceptions.RequestException: return {"error": f"CVE non trouvée sur SUSE"}
    except Exception as e: return {"error": f"Erreur d'analyse HTML SUSE : {e}"}


# --- MODIFIÉ --- Fonction Mistral mise à jour avec votre syntaxe
def get_john_explanation(cve_id):
    # Lit la clé depuis une variable d'environnement.
    # Si non trouvée, utilise la valeur par défaut pour vous indiquer où la mettre.
    api_key = "GYtqLEZ1UShCEejPI8C56v8YIUl38LN0"
    
    if not api_key or api_key == "METTRE_VOTRE_CLÉ_API_MISTRAL_ICI":
        return {'error': "Clé API Mistral non configurée.\n\nDéfinissez la variable d'environnement MISTRAL_API_KEY\nou modifiez le code dans la fonction get_john_explanation."}

    client = Mistral(api_key=api_key)
    model = "mistral-small-latest"
    prompt = f"Explique la vulnérabilité {cve_id} de manière très courte, simple et claire. Adresse-toi à un public non-technique en français. Quel est le risque principal en une phrase ?"
    
    try:
        # Utilisation de la méthode qui fonctionne pour vous
        chat_response = client.chat.complete(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return {'explanation': chat_response.choices[0].message.content}
    except Exception as e:
        return {'error': f"Erreur API Mistral : {e}"}


# --- Application CustomTkinter ---
class CveAnalysisTool(customtkinter.CTk):
    HISTORY_FILE = "history.json"
    KANBAN_FILE = "kanban_data.json"

    def __init__(self):
        super().__init__()
        self.title("CVE Workflow Manager")
        self.geometry("1100x800")
        self.unique_links = []
        self.history = []
        self.kanban_data = {"todo": [], "done": []}
        self.dragged_card = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.mono_font = customtkinter.CTkFont(family="Consolas", size=14, weight="bold")
        self.kanban_card_font = customtkinter.CTkFont(family="Arial", size=16, weight="bold")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.main_tab_view = customtkinter.CTkTabview(self, corner_radius=10)
        self.main_tab_view.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self.main_tab_view.add("Tableau Kanban")
        self.main_tab_view.add("Analyse CVE")
        self.create_kanban_tab()
        self.create_analysis_main_tab()
        self.load_history()
        self.load_kanban_data()
        self.populate_kanban_board()

    def create_kanban_tab(self):
        kanban_tab = self.main_tab_view.tab("Tableau Kanban")
        kanban_tab.grid_columnconfigure(0, weight=1)
        kanban_tab.grid_rowconfigure(2, weight=1)
        add_frame = customtkinter.CTkFrame(kanban_tab, fg_color="transparent")
        add_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        add_frame.grid_columnconfigure(0, weight=1) # --- CORRIGÉ --- S'assure que l'entry prend la largeur
        self.kanban_cve_entry = customtkinter.CTkEntry(add_frame, placeholder_text="Ajouter une CVE au Kanban (ex: CVE-2024-...)")
        self.kanban_cve_entry.grid(row=0, column=0, sticky="ew", padx=(0,10))
        self.kanban_cve_entry.bind("<Return>", self.add_cve_to_kanban)
        add_button = customtkinter.CTkButton(add_frame, text="Ajouter", width=100, command=self.add_cve_to_kanban)
        add_button.grid(row=0, column=1)
        columns_frame = customtkinter.CTkFrame(kanban_tab, fg_color="transparent")
        columns_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(10,0))
        columns_frame.grid_columnconfigure(0, weight=1)
        columns_frame.grid_columnconfigure(1, weight=1)
        columns_frame.grid_rowconfigure(0, weight=1)
        self.todo_column = customtkinter.CTkScrollableFrame(columns_frame, label_text="À faire", label_text_color="#E0E0E0", fg_color="#2c3e50")
        self.todo_column.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        self.done_column = customtkinter.CTkScrollableFrame(columns_frame, label_text="Terminé", label_text_color="#E0E0E0", fg_color="#1f2833")
        self.done_column.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

    def add_cve_to_kanban(self, event=None):
        cve_id = self.kanban_cve_entry.get().strip().upper()
        if not re.match(r'CVE-\d{4}-\d{4,}', cve_id, re.IGNORECASE):
            messagebox.showwarning("Entrée invalide", "Veuillez entrer un identifiant de CVE valide.")
            return
        if cve_id in self.kanban_data["todo"] or cve_id in self.kanban_data["done"]:
            messagebox.showinfo("Info", f"La CVE {cve_id} est déjà dans le tableau.")
            return
        self.kanban_data["todo"].insert(0, cve_id)
        self.save_kanban_data()
        self.populate_kanban_board()
        self.kanban_cve_entry.delete(0, "end")

    def populate_kanban_board(self):
        for col in [self.todo_column, self.done_column]:
            for widget in col.winfo_children(): widget.destroy()
        for cve_id in self.kanban_data["todo"]: self.create_kanban_card(cve_id, self.todo_column)
        for cve_id in self.kanban_data["done"]: self.create_kanban_card(cve_id, self.done_column)

    def create_kanban_card(self, cve_id, parent_column):
        card = customtkinter.CTkFrame(parent_column, border_width=2, border_color="#45a29e", corner_radius=8)
        card.pack(fill="x", padx=10, pady=5)
        card.grid_columnconfigure(0, weight=1)
        card.cve_id = cve_id
        label = customtkinter.CTkLabel(card, text=cve_id, font=self.kanban_card_font, anchor="w")
        label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        button = customtkinter.CTkButton(card, text="Analyser", width=80, fg_color="#66fcf1", text_color="#0b0c10", command=lambda c=cve_id: self.analyze_from_kanban(c))
        button.grid(row=0, column=1, padx=10, pady=10)
        for widget in [card, label]:
            widget.bind("<ButtonPress-1>", self.on_drag_start)
            widget.bind("<B1-Motion>", self.on_drag_motion)
            widget.bind("<ButtonRelease-1>", self.on_drag_stop)

    def analyze_from_kanban(self, cve_id):
        self.cve_entry.delete(0, "end")
        self.cve_entry.insert(0, cve_id)
        self.main_tab_view.set("Analyse CVE")
        self.start_analysis_thread()

    # --- CORRIGÉ --- Logique de détection de la carte améliorée
    def on_drag_start(self, event):
        widget = event.widget
        # Remonter la hiérarchie pour trouver la carte parente (qui a l'attribut cve_id)
        while widget is not None and not hasattr(widget, 'cve_id'):
            widget = widget.master

        # Si aucune carte n'est trouvée (clic en dehors), ne rien faire
        if widget is None:
            self.dragged_card = None
            return

        self.dragged_card = widget
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_drag_motion(self, event):
        if not self.dragged_card: return
        x = self.dragged_card.winfo_x() - self.drag_start_x + event.x
        y = self.dragged_card.winfo_y() - self.drag_start_y + event.y
        self.dragged_card.place(x=x, y=y)

    # --- CORRIGÉ --- Vérification pour éviter l'erreur si dragged_card est None
    def on_drag_stop(self, event):
        if not self.dragged_card: return

        x_root, y_root = event.x_root, event.y_root
        cve_id = self.dragged_card.cve_id
        source_list = None
        if cve_id in self.kanban_data["todo"]:
            self.kanban_data["todo"].remove(cve_id)
            source_list = "todo"
        elif cve_id in self.kanban_data["done"]:
            self.kanban_data["done"].remove(cve_id)
            source_list = "done"

        if self.is_within_widget(self.done_column, x_root, y_root):
            self.kanban_data["done"].insert(0, cve_id)
        elif self.is_within_widget(self.todo_column, x_root, y_root):
            self.kanban_data["todo"].insert(0, cve_id)
        else:
            if source_list: self.kanban_data[source_list].insert(0, cve_id)

        self.dragged_card = None
        self.save_kanban_data()
        self.populate_kanban_board()

    def is_within_widget(self, widget, x_root, y_root):
        x1, y1 = widget.winfo_rootx(), widget.winfo_rooty()
        x2, y2 = x1 + widget.winfo_width(), y1 + widget.winfo_height()
        return x1 <= x_root <= x2 and y1 <= y_root <= y2

    def load_kanban_data(self):
        if os.path.exists(self.KANBAN_FILE):
            try:
                with open(self.KANBAN_FILE, 'r') as f: self.kanban_data = json.load(f)
            except json.JSONDecodeError: self.kanban_data = {"todo": [], "done": []}

    def save_kanban_data(self):
        with open(self.KANBAN_FILE, 'w') as f: json.dump(self.kanban_data, f, indent=4)

    # --- Le reste de l'application (section analyse) reste identique ---
    # ... (toutes les fonctions de create_analysis_main_tab à clear_references) ...
    def create_analysis_main_tab(self):
        analysis_tab=self.main_tab_view.tab("Analyse CVE")
        analysis_tab.grid_columnconfigure(0, weight=1)
        analysis_tab.grid_rowconfigure(1, weight=1)
        input_frame = customtkinter.CTkFrame(analysis_tab, corner_radius=12, fg_color="#1f2833")
        input_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
        input_frame.grid_columnconfigure(1, weight=1)
        cve_label = customtkinter.CTkLabel(input_frame, text="Identifiant CVE :", text_color="#66fcf1", font=("Arial", 14, "bold"))
        cve_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.cve_entry = customtkinter.CTkEntry(input_frame, placeholder_text="Ex: CVE-2024-12345", font=("Arial", 14))
        self.cve_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.cve_entry.bind("<Return>", self.start_analysis_thread)
        self.analyze_button = customtkinter.CTkButton(input_frame, text="Analyser", fg_color="#45a29e", hover_color="#66fcf1", text_color="white", font=("Arial", 14, "bold"), command=self.start_analysis_thread)
        self.analyze_button.grid(row=0, column=2, padx=10, pady=10)
        self.analysis_tab_view = customtkinter.CTkTabview(analysis_tab, corner_radius=12)
        self.analysis_tab_view.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0,15))
        self.analysis_tab_view.add("Analyse des Scores")
        self.analysis_tab_view.add("John make it clear")
        self.analysis_tab_view.add("Références NVD")
        self.analysis_tab_view.add("Historique")
        self.create_scores_tab()
        self.create_john_tab()
        self.create_references_tab()
        self.create_history_tab()
    def create_scores_tab(self):
        tab=self.analysis_tab_view.tab("Analyse des Scores")
        self.results_textbox = customtkinter.CTkTextbox(tab, wrap="word", font=self.mono_font, corner_radius=10)
        self.results_textbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.results_textbox.configure(state="disabled", text_color="#66fcf1", fg_color="#0b0c10")
    def create_john_tab(self):
        tab=self.analysis_tab_view.tab("John make it clear")
        john_font=customtkinter.CTkFont(family="Arial", size=15)
        self.john_textbox = customtkinter.CTkTextbox(tab, wrap="word", font=john_font, corner_radius=10)
        self.john_textbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.john_textbox.configure(state="disabled", text_color="#c5c6c7", fg_color="#0b0c10")
    def create_references_tab(self):
        tab=self.analysis_tab_view.tab("Références NVD")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        ref_header_frame=customtkinter.CTkFrame(tab, fg_color="transparent")
        ref_header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        ref_header_frame.grid_columnconfigure(0, weight=1)
        self.ref_count_label = customtkinter.CTkLabel(ref_header_frame, text="Aucune analyse lancée.", font=("Arial", 12, "italic"))
        self.ref_count_label.grid(row=0, column=0, sticky="w")
        self.open_links_button = customtkinter.CTkButton(ref_header_frame, text="Ouvrir tous les liens", command=self.open_all_links, state="disabled")
        self.open_links_button.grid(row=0, column=1, sticky="e")
        self.ref_scrollable_frame = customtkinter.CTkScrollableFrame(tab, label_text="Liens Uniques", fg_color="#1f2833")
        self.ref_scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
    def create_history_tab(self):
        tab=self.analysis_tab_view.tab("Historique")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        history_header_frame=customtkinter.CTkFrame(tab, fg_color="transparent")
        history_header_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        clear_button=customtkinter.CTkButton(history_header_frame, text="Effacer l'historique", fg_color="#c0392b", hover_color="#e74c3c", command=self.clear_history)
        clear_button.pack(side="right")
        self.history_scrollable_frame = customtkinter.CTkScrollableFrame(tab, label_text="Recherches Récentes")
        self.history_scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
    def start_analysis_thread(self, event=None):
        cve_id=self.cve_entry.get().strip().upper()
        if not re.match(r'CVE-\d{4}-\d{4,}', cve_id, re.IGNORECASE):
            messagebox.showwarning("Entrée invalide", "Veuillez entrer un identifiant de CVE valide.")
            return
        self.analyze_button.configure(state="disabled", text="Analyse...")
        self.update_results(f"Analyse en cours pour {cve_id}...")
        self.clear_references()
        self.update_john_explanation("John réfléchit...")
        thread = Thread(target=self.run_analysis, args=(cve_id,), daemon=True)
        thread.start()
    def run_analysis(self, cve_id):
        nvd_result=get_nvd_data(cve_id)
        suse_result=get_suse_score(cve_id)
        john_result=get_john_explanation(cve_id)
        if 'error' not in nvd_result:
            self.after(0, self.add_to_history, cve_id)
        self.after(0, self.display_all_results, cve_id, nvd_result, suse_result, john_result)
    def display_all_results(self, cve_id, nvd_result, suse_result, john_result):
        self.analyze_button.configure(state="normal", text="Analyser")
        self.display_scores(cve_id, nvd_result, suse_result)
        self.display_references(nvd_result)
        self.display_john_explanation(john_result)
        self.analysis_tab_view.set("Analyse des Scores")
    def load_history(self):
        if os.path.exists(self.HISTORY_FILE):
            try:
                with open(self.HISTORY_FILE, 'r') as f: self.history = json.load(f)
                self.populate_history_tab()
            except json.JSONDecodeError: self.history = []
    def save_history(self):
        with open(self.HISTORY_FILE, 'w') as f: json.dump(self.history, f, indent=4)
    def add_to_history(self, cve_id):
        if cve_id in self.history: self.history.remove(cve_id)
        self.history.insert(0, cve_id)
        self.history = self.history[:50]
        self.save_history()
        self.populate_history_tab()
    def populate_history_tab(self):
        for widget in self.history_scrollable_frame.winfo_children(): widget.destroy()
        for cve in self.history:
            btn = customtkinter.CTkButton(self.history_scrollable_frame, text=cve, command=lambda c=cve: self.re_analyze(c), anchor="w")
            btn.pack(fill="x", padx=5, pady=2)
    def re_analyze(self, cve_id):
        self.cve_entry.delete(0, "end")
        self.cve_entry.insert(0, cve_id)
        self.start_analysis_thread()
    def clear_history(self):
        if messagebox.askyesno("Confirmation", "Effacer tout l'historique ?"):
            self.history = []
            self.save_history()
            self.populate_history_tab()
    def display_scores(self, cve_id, nvd_result, suse_result):
        text = f"Analyse pour {cve_id.upper()}\n{'='*70}\n\n"
        text += "--- Source : NVD (National Vulnerability Database) ---\n"
        nvd_score, nvd_vector = None, None
        
        if 'error' in nvd_result:
            text += f"Erreur : {nvd_result['error']}\n"
        elif 'error_score' in nvd_result:
            text += f"Score : {nvd_result['error_score']}\n"
        else:
            nvd_score, nvd_vector = nvd_result.get('score'), nvd_result.get('vecteur')
            text += f"Score : {nvd_score} ({nvd_result.get('severite')}) - {nvd_result.get('version')}\n"
            text += f"Vecteur : {nvd_vector}\n\n"
            text += parse_and_explain_vector(nvd_vector)
        
        text += f"\n\n{'='*70}\n\n"
        text += "--- Source : SUSE ---\n"
        if 'error' in suse_result:
            text += f"Erreur : {suse_result['error']}\n"
        else:
            suse_key = list(suse_result.keys())[0]
            suse_data = suse_result[suse_key]
            suse_score_str = suse_data.get('score', '0.0')
            suse_vector_core = suse_data.get('vector', '')
            nvd_vector_core = nvd_vector.split('/', 1)[1] if nvd_vector and '/' in nvd_vector else nvd_vector
            
            if nvd_score is not None and float(nvd_score) == float(suse_score_str) and nvd_vector_core == suse_vector_core:
                 text += "Le score et le vecteur SUSE sont IDENTIQUES à ceux du NVD.\n"
            else:
                if nvd_score is not None:
                     text += "⚠️ ATTENTION : Différence détectée avec le score NVD.\n\n"
                
                suse_version_str = suse_key.replace('v', '')
                text += f"Score SUSE : {suse_score_str} (CVSS {suse_version_str})\n"
                full_suse_vector = f"CVSS:{suse_version_str}/{suse_vector_core}"
                text += f"Vecteur SUSE : {full_suse_vector}\n\n"
                text += parse_and_explain_vector(suse_vector_core)
        
        self.update_results(text)
    def display_references(self, nvd_result):
        self.clear_references()
        if 'error' in nvd_result or not nvd_result.get('references'):
            self.ref_count_label.configure(text="Aucune référence trouvée.")
            return
        all_urls=[ref.get('url') for ref in nvd_result['references'] if ref.get('url')]
        self.unique_links = sorted(set(all_urls))
        if not self.unique_links:
            self.ref_count_label.configure(text="Aucune référence trouvée.")
            return
        self.ref_count_label.configure(text=f"{len(self.unique_links)} références uniques.")
        self.open_links_button.configure(state="normal")
        for idx, url in enumerate(self.unique_links, start=1):
            link_label=customtkinter.CTkLabel(self.ref_scrollable_frame, text=f"{idx}. {url}", text_color="#45a29e", cursor="hand2", wraplength=900, justify="left")
            link_label.pack(anchor="w", padx=10, pady=5)
            link_label.bind("<Button-1>", lambda e, link=url: webbrowser.open(link))
    def display_john_explanation(self, john_result):
        if 'error' in john_result: text=f"John n'a pas pu répondre :\n\n{john_result['error']}"
        else: text=john_result.get('explanation', "John est resté silencieux.")
        self.update_john_explanation(text)
    def open_all_links(self):
        if not self.unique_links: return
        if messagebox.askyesno("Confirmation", f"Ouvrir {len(self.unique_links)} onglets ?"):
            for link in self.unique_links: webbrowser.open_new_tab(link)
    def update_results(self, text):
        self.results_textbox.configure(state="normal")
        self.results_textbox.delete("1.0", "end")
        self.results_textbox.insert("1.0", text)
        self.results_textbox.configure(state="disabled")
    def update_john_explanation(self, text):
        self.john_textbox.configure(state="normal")
        self.john_textbox.delete("1.0", "end")
        self.john_textbox.insert("1.0", text)
        self.john_textbox.configure(state="disabled")
    def clear_references(self):
        for widget in self.ref_scrollable_frame.winfo_children(): widget.destroy()
        self.ref_count_label.configure(text="Aucune analyse lancée.")
        self.open_links_button.configure(state="disabled")
        self.unique_links = []

if __name__ == "__main__":
    app = CveAnalysisTool()
    app.mainloop()