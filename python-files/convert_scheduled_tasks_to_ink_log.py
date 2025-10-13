```python
import pandas as pd
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import openpyxl
from openpyxl.utils import get_column_letter

def assign_shift(start_time):
    """Assign shift based on time (6:00 AM–6:00 PM = Shift 1, 6:00 PM–6:00 AM = Shift 2)."""
    hour = start_time.hour
    if 6 <= hour < 18:
        return 1
    else:
        return 2

def convert_to_ink_log():
    try:
        # Read ScheduledTasks Excel file
        tasks_df = pd.read_excel("ScheduledTasks (8).xlsx")

        # Filter for completed jobs
        completed_jobs = tasks_df[tasks_df['Task Status'] == 'Completed']

        # Initialize Ink Log columns
        ink_log_data = {
            'Date': [],
            'Shift': [],
            'Press #': [],
            'Order #': [],
            'Description': [],
            '': ['', '', '', '', '', '', '', '', '', '', ''],  # Empty columns
            '# Colors': [],
            '# Pulls': [],
            'Ink Time': [],
            'N/R': [],
            'A': [], 'B': [], 'C': [], 'D': [], 'E': [], 'F': [], 'G': [], 'H': [], 'I': [], 'J': [], 'K': [], 'L': [],
            'Notes': []
        }

        # Process each completed job
        for _, row in completed_jobs.iterrows():
            # Convert date to MM/DD/YYYY
            task_date = pd.to_datetime(row['Task Start Date']).strftime('%m/%d/%Y')
            # Assign shift
            shift = assign_shift(pd.to_datetime(row['Task Start Date']))
            # Map press
            press = {'PRESS8': 8, 'P5': 5, 'P6': 6}.get(row['Cost Center Code'], 8)

            # Append to Ink Log
            ink_log_data['Date'].append(task_date)
            ink_log_data['Shift'].append(shift)
            ink_log_data['Press #'].append(press)
            ink_log_data['Order #'].append(row['Job Code'])
            ink_log_data['Description'].append(row['Job Description'])
            ink_log_data['# Colors'].append(6)  # Assume 6 colors
            ink_log_data['# Pulls'].append(0)
            ink_log_data['Ink Time'].append(0)
            ink_log_data['N/R'].append('R')
            ink_log_data['A'].append(0)
            ink_log_data['B'].append(0)
            ink_log_data['C'].append(0)
            ink_log_data['D'].append(0)
            ink_log_data['E'].append(0)
            ink_log_data['F'].append(0)
            ink_log_data['G'].append(0)
            ink_log_data['H'].append(0)
            ink_log_data['I'].append(0)
            ink_log_data['J'].append(0)
            ink_log_data['K'].append(0)
            ink_log_data['L'].append(0)
            ink_log_data['Notes'].append('All colors passed')

        # Create DataFrame
        ink_log_df = pd.DataFrame(ink_log_data)

        # Load existing Ink Log Excel file
        wb = openpyxl.load_workbook("Dominion Sinkro KPI Report 2025.xlsx")
        ws = wb['Oct']

        # Find the last row with data in the Ink Log (before summary)
        last_row = 6
        for row in range(7, ws.max_row):
            if ws[f'A{row}'].value is None or ws[f'A{row}'].value == '':
                break
            last_row = row

        # Append new rows starting from row 7 or after existing data
        start_row = max(7, last_row + 1)
        for i, row in ink_log_df.iterrows():
            for j, col in enumerate(ink_log_df.columns):
                ws[f'{get_column_letter(j+1)}{start_row+i}'] = row[col]

        # Update summary statistics (rows 162–176)
        new_jobs = len(ink_log_df)
        press_8_jobs = len(ink_log_df[ink_log_df['Press #'] == 8]) + 14  # Original 14
        press_5_jobs = len(ink_log_df[ink_log_df['Press #'] == 5]) + 0   # Original 0
        press_6_jobs = len(ink_log_df[ink_log_df['Press #'] == 6]) + 3   # Original 3
        shift_1_jobs = len(ink_log_df[ink_log_df['Shift'] == 1]) + 1      # Original 1
        shift_2_jobs = len(ink_log_df[ink_log_df['Shift'] == 2]) + 12     # Original 12
        shift_3_jobs = 4  # Original 4
        shift_4_jobs = 0  # Original 0
        total_jobs = new_jobs + 17  # Original 17
        total_ink_time = 60  # Original 60 + 0 new ink time
        jobs_0_pulls = len(ink_log_df[ink_log_df['# Pulls'] == 0]) + 13  # Original 13
        percent_0_pulls = jobs_0_pulls / total_jobs if total_jobs > 0 else 0
        total_colors = (6 * new_jobs) + 96  # Original 96
        avg_colors = total_colors / total_jobs if total_jobs > 0 else 0
        total_pulls = 1  # Original 1 + 0 new pulls
        avg_pulls = total_pulls / total_jobs if total_jobs > 0 else 0
        avg_mins_job = total_ink_time / total_jobs if total_jobs > 0 else 0
        avg_mins_col = total_ink_time / total_colors if total_colors > 0 else 0
        avg_mins_pull = total_ink_time / total_pulls if total_pulls > 0 else 0

        # Write summary statistics
        ws['A162'] = 'Press 8 Jobs:'
        ws['D162'] = press_8_jobs
        ws['I162'] = 'Total Ink Time (minutes):'
        ws['M162'] = total_ink_time
        ws['A163'] = 'Press 5 Jobs:'
        ws['D163'] = press_5_jobs
        ws['I163'] = 'Broken Down:'
        ws['M163'] = 'mins'
        ws['N163'] = '%'
        ws['A164'] = 'Press 6 Jobs:'
        ws['D164'] = press_6_jobs
        ws['I164'] = 'A - ink off shade:'
        ws['M164'] = 30  # Unchanged
        ws['N164'] = 0.5  # Unchanged
        ws['C165'] = 1
        ws['D165'] = shift_1_jobs
        ws['E165'] = total_jobs
        ws['I165'] = 'B - wrong color info:'
        ws['M165'] = 0
        ws['N165'] = 0
        ws['C166'] = 2
        ws['D166'] = shift_2_jobs
        ws['I166'] = 'C - process color match:'
        ws['M166'] = 0
        ws['N166'] = 0
        ws['C167'] = 3
        ws['D167'] = shift_3_jobs
        ws['I167'] = 'D - dirty equipment:'
        ws['M167'] = 0
        ws['N167'] = 0
        ws['C168'] = 4
        ws['D168'] = shift_4_jobs
        ws['I168'] = 'E - wrong anilox:'
        ws['M168'] = 0
        ws['N168'] = 0
        ws['A169'] = 'Total Jobs:'
        ws['D169'] = total_jobs
        ws['I169'] = 'F - change anilox:'
        ws['M169'] = 0
        ws['N169'] = 0
        ws['A170'] = "Average # of Col's:"
        ws['D170'] = avg_colors
        ws['I170'] = 'G - wrong ink viscosity:'
        ws['M170'] = 0
        ws['N170'] = 0
        ws['A171'] = 'Average # of Pulls:'
        ws['D171'] = avg_pulls
        ws['I171'] = 'H - customer approval:'
        ws['M171'] = 0
        ws['N171'] = 0
        ws['A172'] = 'Average mins/col:'
        ws['D172'] = avg_mins_col
        ws['I172'] = 'I - new job:'
        ws['M172'] = 0
        ws['N172'] = 0
        ws['A173'] = 'Average mins/pull:'
        ws['D173'] = avg_mins_pull
        ws['I173'] = 'J - plate issues:'
        ws['M173'] = 0
        ws['N173'] = 0
        ws['A174'] = 'Average mins/job:'
        ws['D174'] = avg_mins_job
        ws['I174'] = 'K - Other:'
        ws['M174'] = 0
        ws['N174'] = 0
        ws['A175'] = 'Jobs 0 Color Pulls'
        ws['D175'] = jobs_0_pulls
        ws['I175'] = 'L - ink time during run'
        ws['M175'] = 30
        ws['N175'] = 0.5
        ws['A176'] = '% Jobs 0 Col Pulls'
        ws['D176'] = percent_0_pulls
        ws['I176'] = 'L - ink time during run'
        ws['M176'] = 30
        ws['N176'] = 0.5

        # Save the updated Excel file
        wb.save("Dominion Sinkro KPI Report 2025_updated.xlsx")
        messagebox.showinfo("Success", "Conversion completed! Output saved to 'Dominion Sinkro KPI Report 2025_updated.xlsx'")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Create GUI
root = tk.Tk()
root.title("ScheduledTasks to Ink Log Converter")
root.geometry("300x150")

# Add a button to trigger conversion
convert_button = tk.Button(root, text="Convert ScheduledTasks to Ink Log", command=convert_to_ink_log, font=("Arial", 12))
convert_button.pack(pady=50)

# Run the GUI
root.mainloop()
```