import tkinter as tk
from tkinter import ttk
import datetime

class MaterialReport:
    def __init__(self, root):
        self.root = root
        self.root.title("МАТЕРИАЛЬНЫЙ ОТЧЕТ")
        self.root.geometry("1400x800")
        
        # Данные для хранения значений
        self.days_data = []
        self.initial_balance = 12786627
        
        self.create_widgets()
        
    def create_widgets(self):
        # Основной фрейм с прокруткой
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заголовок
        title_label = tk.Label(main_frame, text="МАТЕРИАЛЬНЫЙ ОТЧЕТ", 
                              font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=23, pady=10)
        
        # Информация о магазине
        shop_label = tk.Label(main_frame, text='Магазин : "СЕВЕРНЫЙ" САМУР-СИТИ',
                             font=("Arial", 12))
        shop_label.grid(row=1, column=0, columnspan=23, pady=5)
        
        # Остаток товара
        balance_label = tk.Label(main_frame, text="Остаток товара на:", font=("Arial", 10))
        balance_label.grid(row=2, column=0, sticky="w")
        
        self.date_var = tk.StringVar(value="2025-09-01")
        date_entry = tk.Entry(main_frame, textvariable=self.date_var, width=12)
        date_entry.grid(row=2, column=1, padx=5)
        
        balance_value_label = tk.Label(main_frame, text="Сумма", font=("Arial", 10))
        balance_value_label.grid(row=2, column=2, sticky="w")
        
        self.balance_var = tk.StringVar(value=str(self.initial_balance))
        balance_entry = tk.Entry(main_frame, textvariable=self.balance_var, width=15)
        balance_entry.grid(row=2, column=3, padx=5)
        
        # Заголовки столбцов
        headers = [
            "Дата", "Продукты", "Фрукты", "Сигарети", "Соки, Молоко", "Химия",
            "Игрушки Диваны", "Хлеб", "Булочка вес.", "Зелень", "Батамай молочка",
            "Самса", "Дед-Мороз", "Капуста Кваш.", "Уценка+ Приход", "Наценка",
            "Выручка", "Терминал; QR-Код.", "Возврат товара", "Списание товара",
            "Списание Оптовый", "Диван списание", "Скидки; Самса-Арам; Столовая.", "Столовая"
        ]
        
        # Создаем заголовки
        for col, header in enumerate(headers):
            label = tk.Label(main_frame, text=header, font=("Arial", 8, "bold"), 
                           borderwidth=1, relief="solid", bg="lightgray")
            label.grid(row=4, column=col, sticky="nsew", padx=1, pady=1)
        
        # Поля для ввода данных за каждый день
        self.entries = []
        for day in range(30):  # 30 дней
            day_entries = []
            row = day + 5
            
            # Дата
            date_var = tk.StringVar(value=f"2025-09-{day+1:02d}")
            date_entry = tk.Entry(main_frame, textvariable=date_var, width=12)
            date_entry.grid(row=row, column=0, padx=1, pady=1)
            day_entries.append(date_var)
            
            # Числовые поля
            for col in range(1, len(headers)):
                var = tk.StringVar(value="0")
                entry = tk.Entry(main_frame, textvariable=var, width=12)
                entry.grid(row=row, column=col, padx=1, pady=1)
                entry.bind('<KeyRelease>', self.calculate_totals)
                day_entries.append(var)
            
            self.entries.append(day_entries)
        
        # Кнопка расчета
        calc_button = tk.Button(main_frame, text="Рассчитать итоги", 
                               command=self.calculate_totals, bg="lightblue")
        calc_button.grid(row=35, column=0, columnspan=5, pady=10)
        
        # Поля для итогов
        totals_row = 37
        tk.Label(main_frame, text="ИТОГО", font=("Arial", 10, "bold")).grid(row=totals_row, column=0)
        
        self.total_vars = []
        for col in range(1, len(headers)):
            var = tk.StringVar(value="0")
            label = tk.Label(main_frame, textvariable=var, font=("Arial", 9, "bold"),
                           borderwidth=1, relief="solid", bg="white")
            label.grid(row=totals_row, column=col, sticky="nsew", padx=1, pady=1)
            self.total_vars.append(var)
        
        # Остатки
        balance_row = 38
        tk.Label(main_frame, text="ОСТАТОК", font=("Arial", 10, "bold")).grid(row=balance_row, column=0)
        
        self.final_balance_var = tk.StringVar(value="0")
        balance_label = tk.Label(main_frame, textvariable=self.final_balance_var, 
                               font=("Arial", 9, "bold"), borderwidth=1, relief="solid")
        balance_label.grid(row=balance_row, column=1, columnspan=5, sticky="nsew", padx=1, pady=1)
        
        # Настройка весов строк и столбцов для растягивания
        for i in range(40):
            main_frame.grid_rowconfigure(i, weight=1)
        for i in range(23):
            main_frame.grid_columnconfigure(i, weight=1)
    
    def calculate_totals(self, event=None):
        try:
            # Рассчитываем итоги по столбцам
            totals = [0.0] * (len(self.entries[0]) - 1)  # -1 потому что первый элемент - дата
            
            for day_entries in self.entries:
                for i in range(1, len(day_entries)):  # Пропускаем дату
                    try:
                        value = float(day_entries[i].get() or 0)
                        totals[i-1] += value
                    except ValueError:
                        pass
            
            # Обновляем итоги
            for i, var in enumerate(self.total_vars):
                var.set(f"{totals[i]:.2f}")
            
            # Рассчитываем конечный остаток
            initial = float(self.balance_var.get() or 0)
            
            # Основные приходы (столбцы 1-13)
            main_income = sum(totals[0:13])
            
            # Выручка и другие движения (столбцы 15-22)
            revenue_and_other = totals[15] + totals[17] + totals[18] + totals[19] + totals[20] + totals[21] + totals[22]
            
            final_balance = initial + main_income - revenue_and_other
            self.final_balance_var.set(f"{final_balance:.2f}")
            
        except Exception as e:
            print(f"Ошибка расчета: {e}")

def main():
    root = tk.Tk()
    app = MaterialReport(root)
    root.mainloop()

if __name__ == "__main__":
    main()
