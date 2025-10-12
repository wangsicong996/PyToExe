import datetime
import random
import time
import tkinter as tk
from tkinter import ttk, messagebox
import threading

class TerminalPlatniczy:
    def platnosc_karta(self, kwota, typ_biletu, strefa):
        print(f"\n💳 TERMINAL PŁATNICZY - KARTA")
        print(f"Kwota: {kwota:.2f} zł | {typ_biletu} | {strefa}")
        print("Przykład karty...")
        time.sleep(2)
        
        if random.random() < 0.95:
            return True, "Płatność kartą zatwierdzona"
        else:
            return False, "Płatność odrzucona"

    def platnosc_gotowka(self, kwota, typ_biletu, strefa):
        print(f"\n💵 PŁATNOŚĆ GOTÓWKĄ")
        print(f"Kwota: {kwota:.2f} zł | {typ_biletu} | {strefa}")
        return True, "Płatność gotówką przyjęta"

class SystemSprzedazyBiletow:
    def __init__(self):
        self.ceny_biletow_jednorazowe = {
            '1': 1.00,
            '1+2': 2.00,
            '1+3': 4.00
        }
        
        self.ceny_biletow_okresowe = {
            '1_30dni': 30.00,
            '1+2_30dni': 65.00,
            '1+3_30dni': 80.00
        }
        
        self.sprzedaz_dzisiaj = {
            'jednorazowe': 0,
            'okresowe': 0,
            'kwota': 0.0
        }
        
        self.historia_transakcji = []
        self.terminal = TerminalPlatniczy()
        
        # Inicjalizacja GUI
        self.inicjalizuj_gui()

    def inicjalizuj_gui(self):
        self.root = tk.Tk()
        self.root.title("System Sprzedaży Biletów KM")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        self.stworz_interfejs()

    def stworz_interfejs(self):
        # Nagłówek
        naglowek_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        naglowek_frame.pack(fill='x', padx=10, pady=10)
        naglowek_frame.pack_propagate(False)
        
        tk.Label(naglowek_frame, text="🚍 SYSTEM SPRZEDAŻY BILETÓW", 
                font=('Arial', 20, 'bold'), fg='white', bg='#2c3e50').pack(expand=True)
        
        # Główne okno
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Przyciski główne
        btn_frame = tk.Frame(main_frame, bg='#f0f0f0')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="🎫 BILETY JEDNORAZOWE", 
                 command=self.pokaz_bilety_jednorazowe,
                 font=('Arial', 14), bg='#3498db', fg='white',
                 width=25, height=2).grid(row=0, column=0, padx=10, pady=10)
        
        tk.Button(btn_frame, text="📅 BILETY OKRESOWE", 
                 command=self.pokaz_bilety_okresowe,
                 font=('Arial', 14), bg='#e74c3c', fg='white',
                 width=25, height=2).grid(row=0, column=1, padx=10, pady=10)
        
        tk.Button(btn_frame, text="📊 STATYSTYKI", 
                 command=self.pokaz_statystyki_gui,
                 font=('Arial', 14), bg='#27ae60', fg='white',
                 width=25, height=2).grid(row=1, column=0, padx=10, pady=10)
        
        tk.Button(btn_frame, text="📋 HISTORIA", 
                 command=self.pokaz_historie_gui,
                 font=('Arial', 14), bg='#f39c12', fg='white',
                 width=25, height=2).grid(row=1, column=1, padx=10, pady=10)
        
        # Panel informacyjny
        self.info_frame = tk.Frame(main_frame, bg='#ecf0f1', relief='solid', bd=1)
        self.info_frame.pack(fill='both', expand=True, pady=20)
        
        self.info_text = tk.Text(self.info_frame, height=15, font=('Arial', 10),
                                bg='#ecf0f1', wrap='word')
        scrollbar = tk.Scrollbar(self.info_frame, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=scrollbar.set)
        
        self.info_text.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y')
        
        # Stopka
        stopka_frame = tk.Frame(self.root, bg='#34495e', height=40)
        stopka_frame.pack(fill='x', side='bottom')
        stopka_frame.pack_propagate(False)
        
        tk.Label(stopka_frame, text="System Sprzedaży Biletów v2.0 © 2024",
                font=('Arial', 10), fg='white', bg='#34495e').pack(expand=True)

    def pokaz_bilety_jednorazowe(self):
        self.wyczysc_info()
        self.info_text.insert('end', "🎫 BILETY JEDNORAZOWE\n" + "="*40 + "\n\n")
        
        for i, (strefa, cena) in enumerate(self.ceny_biletow_jednorazowe.items(), 1):
            self.info_text.insert('end', f"{i}. Strefa {strefa} - {cena:.2f} zł\n")
        
        self.info_text.insert('end', "\n" + "="*40 + "\n")
        
        # Przyciski wyboru biletu
        btn_frame = tk.Frame(self.info_frame, bg='#ecf0f1')
        self.info_text.window_create('end', window=btn_frame)
        
        tk.Button(btn_frame, text="Strefa 1 - 1.00 zł", 
                 command=lambda: self.proces_sprzedazy('1', 1.00, 'jednorazowy'),
                 font=('Arial', 12), bg='#3498db', fg='white', width=20).pack(pady=5)
        
        tk.Button(btn_frame, text="Strefy 1+2 - 2.00 zł", 
                 command=lambda: self.proces_sprzedazy('1+2', 2.00, 'jednorazowy'),
                 font=('Arial', 12), bg='#3498db', fg='white', width=20).pack(pady=5)
        
        tk.Button(btn_frame, text="Strefy 1+3 - 4.00 zł", 
                 command=lambda: self.proces_sprzedazy('1+3', 4.00, 'jednorazowy'),
                 font=('Arial', 12), bg='#3498db', fg='white', width=20).pack(pady=5)

    def pokaz_bilety_okresowe(self):
        self.wyczysc_info()
        self.info_text.insert('end', "📅 BILETY OKRESOWE (30 dni)\n" + "="*40 + "\n\n")
        
        for i, (strefa, cena) in enumerate(self.ceny_biletow_okresowe.items(), 1):
            nazwa = strefa.replace('_30dni', '').replace('1', 'Strefa 1').replace('+2', '+2').replace('+3', '+3')
            self.info_text.insert('end', f"{i}. {nazwa} - {cena:.2f} zł\n")
        
        self.info_text.insert('end', "\n" + "="*40 + "\n")
        
        # Przyciski wyboru biletu
        btn_frame = tk.Frame(self.info_frame, bg='#ecf0f1')
        self.info_text.window_create('end', window=btn_frame)
        
        tk.Button(btn_frame, text="Strefa 1 - 30.00 zł", 
                 command=lambda: self.proces_sprzedazy('1', 30.00, 'okresowy'),
                 font=('Arial', 12), bg='#e74c3c', fg='white', width=20).pack(pady=5)
        
        tk.Button(btn_frame, text="Strefy 1+2 - 65.00 zł", 
                 command=lambda: self.proces_sprzedazy('1+2', 65.00, 'okresowy'),
                 font=('Arial', 12), bg='#e74c3c', fg='white', width=20).pack(pady=5)
        
        tk.Button(btn_frame, text="Strefy 1+3 - 80.00 zł", 
                 command=lambda: self.proces_sprzedazy('1+3', 80.00, 'okresowy'),
                 font=('Arial', 12), bg='#e74c3c', fg='white', width=20).pack(pady=5)

    def proces_sprzedazy(self, strefa, kwota, typ_biletu):
        self.wyczysc_info()
        self.info_text.insert('end', f"🛒 PROCES SPRZEDAŻY\n" + "="*40 + "\n\n")
        self.info_text.insert('end', f"Bilet: {typ_biletu.upper()}\n")
        self.info_text.insert('end', f"Strefa: {strefa}\n")
        self.info_text.insert('end', f"Kwota: {kwota:.2f} zł\n\n")
        self.info_text.insert('end', "Wybierz metodę płatności:\n")
        
        # Przyciski płatności
        btn_frame = tk.Frame(self.info_frame, bg='#ecf0f1')
        self.info_text.window_create('end', window=btn_frame)
        
        tk.Button(btn_frame, text="💳 PŁATNOŚĆ KARTĄ", 
                 command=lambda: self.realizuj_platnosc(strefa, kwota, typ_biletu, 'karta'),
                 font=('Arial', 12), bg='#9b59b6', fg='white', width=20).pack(pady=5)
        
        tk.Button(btn_frame, text="💵 PŁATNOŚĆ GOTÓWKĄ", 
                 command=lambda: self.realizuj_platnosc(strefa, kwota, typ_biletu, 'gotowka'),
                 font=('Arial', 12), bg='#2ecc71', fg='white', width=20).pack(pady=5)
        
        tk.Button(btn_frame, text="↩️ POWRÓT", 
                 command=self.pokaz_bilety_jednorazowe if typ_biletu == 'jednorazowy' else self.pokaz_bilety_okresowe,
                 font=('Arial', 12), bg='#95a5a6', fg='white', width=20).pack(pady=5)

    def realizuj_platnosc(self, strefa, kwota, typ_biletu, metoda_platnosci):
        def procesuj_w_watku():
            self.info_text.delete(1.0, 'end')
            self.info_text.insert('end', f"⏳ PRZETWARZANIE PŁATNOŚCI...\n" + "="*40 + "\n\n")
            
            if metoda_platnosci == 'karta':
                sukces, wiadomosc = self.terminal.platnosc_karta(kwota, typ_biletu, strefa)
            else:
                sukces, wiadomosc = self.terminal.platnosc_gotowka(kwota, typ_biletu, strefa)
            
            # Aktualizacja GUI w głównym wątku
            self.root.after(0, lambda: self.zakoncz_platnosc(sukces, wiadomosc, strefa, kwota, typ_biletu, metoda_platnosci))
        
        threading.Thread(target=procesuj_w_watku, daemon=True).start()

    def zakoncz_platnosc(self, sukces, wiadomosc, strefa, kwota, typ_biletu, metoda_platnosci):
        self.wyczysc_info()
        
        if sukces:
            self.info_text.insert('end', f"✅ TRANSAKCJA ZAKOŃCZONA SUKCESEM\n" + "="*40 + "\n\n")
            self.info_text.insert('end', f"{wiadomosc}\n")
            self.info_text.insert('end', f"Metoda: {metoda_platnosci.upper()}\n")
            self.info_text.insert('end', f"Kwota: {kwota:.2f} zł\n\n")
            
            # Aktualizacja statystyk
            if typ_biletu == 'jednorazowy':
                self.sprzedaz_dzisiaj['jednorazowe'] += 1
            else:
                self.sprzedaz_dzisiaj['okresowe'] += 1
            self.sprzedaz_dzisiaj['kwota'] += kwota
            
            # Zapisz w historii
            transakcja = {
                'data': datetime.datetime.now(),
                'typ': typ_biletu,
                'strefa': strefa,
                'kwota': kwota,
                'metoda': metoda_platnosci
            }
            self.historia_transakcji.append(transakcja)
            
            # Wydruk biletu
            self.drukuj_bilet_gui(typ_biletu, strefa, kwota, typ_biletu == 'okresowy')
            
        else:
            self.info_text.insert('end', f"❌ TRANSAKCJA NIEUDANA\n" + "="*40 + "\n\n")
            self.info_text.insert('end', f"{wiadomosc}\n\n")
            self.info_text.insert('end', "Proszę spróbować ponownie.\n")
        
        # Przycisk powrotu
        btn_frame = tk.Frame(self.info_frame, bg='#ecf0f1')
        self.info_text.window_create('end', window=btn_frame)
        
        tk.Button(btn_frame, text="↩️ POWRÓT DO MENU", 
                 command=self.pokaz_bilety_jednorazowe if typ_biletu == 'jednorazowy' else self.pokaz_bilety_okresowe,
                 font=('Arial', 12), bg='#3498db', fg='white', width=20).pack(pady=10)

    def drukuj_bilet_gui(self, typ_biletu, strefa, kwota, czy_okresowy):
        self.info_text.insert('end', "\n🎫 WYDRUK BILETU\n" + "="*30 + "\n")
        self.info_text.insert('end', f"BILET KOMUNIKACJI MIEJSKIEJ\n")
        self.info_text.insert('end', f"Typ: {'OKRESOWY' if czy_okresowy else 'JEDNORAZOWY'}\n")
        self.info_text.insert('end', f"Strefa: {strefa}\n")
        self.info_text.insert('end', f"Cena: {kwota:.2f} zł\n")
        self.info_text.insert('end', f"Data: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        if czy_okresowy:
            data_waznosci = datetime.datetime.now() + datetime.timedelta(days=30)
            self.info_text.insert('end', f"Ważny do: {data_waznosci.strftime('%Y-%m-%d')}\n")
        else:
            self.info_text.insert('end', "Waży: 60 minut od skasowania\n")
        
        self.info_text.insert('end', f"Numer: {random.randint(100000, 999999)}\n")
        self.info_text.insert('end', "="*30 + "\n")

    def pokaz_statystyki_gui(self):
        self.wyczysc_info()
        self.info_text.insert('end', "📊 STATYSTYKI SPRZEDAŻY\n" + "="*40 + "\n\n")
        self.info_text.insert('end', f"Bilety jednorazowe: {self.sprzedaz_dzisiaj['jednorazowe']} szt.\n")
        self.info_text.insert('end', f"Bilety okresowe: {self.sprzedaz_dzisiaj['okresowe']} szt.\n")
        self.info_text.insert('end', f"Łączna kwota: {self.sprzedaz_dzisiaj['kwota']:.2f} zł\n")
        self.info_text.insert('end', f"Łączna liczba transakcji: {len(self.historia_transakcji)}\n\n")
        
        # Szczegółowa historia
        if self.historia_transakcji:
            self.info_text.insert('end', "OSTATNIE TRANSAKCJE:\n" + "-"*30 + "\n")
            for trans in self.historia_transakcji[-5:]:
                self.info_text.insert('end', 
                    f"{trans['data'].strftime('%H:%M')} | "
                    f"{trans['typ'][:3]} | "
                    f"{trans['strefa']} | "
                    f"{trans['kwota']:.2f} zł | "
                    f"{trans['metoda'][:1]}\n")

    def pokaz_historie_gui(self):
        self.wyczysc_info()
        self.info_text.insert('end', "📋 HISTORIA TRANSAKCJI\n" + "="*50 + "\n\n")
        
        if not self.historia_transakcji:
            self.info_text.insert('end', "Brak transakcji do wyświetlenia\n")
            return
        
        for i, trans in enumerate(self.historia_transakcji[-15:], 1):
            self.info_text.insert('end', 
                f"{i:2d}. {trans['data'].strftime('%m-%d %H:%M')} | "
                f"{trans['typ'].upper():10} | "
                f"{trans['strefa']:8} | "
                f"{trans['kwota']:6.2f} zł | "
                f"{trans['metoda'].upper()}\n")

    def wyczysc_info(self):
        self.info_text.delete(1.0, 'end')

    def uruchom(self):
        self.root.mainloop()

# Uruchomienie systemu
if __name__ == "__main__":
    system = SystemSprzedazyBiletow()
    system.uruchom()