import tkinter as tk
from tkinter import messagebox
import win32gui
import win32api
import win32con
import time
import threading

# --- 사용자 설정 ---
VK_CODE = 0x58        # 입력할 키의 Virtual Key Code. 0x58은 'X' 키입니다.
DELAY_SECONDS = 0.1   # 각 키 입력 신호 사이의 딜레이 (초 단위)
# --------------------

def run_macro(hwnd, title, stop_event):
    """백그라운드에서 키 입력을 실행하는 함수 (별도 스레드에서 동작)"""
    print(f"INFO: '{title}' 창에 매크로 스레드를 시작합니다.")
    
    # 'X' 키의 하드웨어 스캔 코드 (더 안정적인 입력을 위해)
    scan_code = 0x2D
    lParam = (scan_code << 16) | 1
    
    # stop_event가 설정되지 않은 동안(중지 신호가 오기 전까지) 반복
    while not stop_event.is_set():
        try:
            # 창이 여전히 존재하는지 확인
            if not win32gui.IsWindow(hwnd):
                print(f"ERROR: 대상 창 '{title}'을 찾을 수 없습니다. 스레드를 종료합니다.")
                break
            
            # PostMessage로 백그라운드에 키 입력 전송
            win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, VK_CODE, lParam)
            time.sleep(DELAY_SECONDS)
        except Exception as e:
            print(f"ERROR: 매크로 실행 중 오류 발생: {e}")
            break
            
    print(f"INFO: '{title}' 창의 매크로 스레드가 정상적으로 중지되었습니다.")


class MacroControlGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("매크로 제어판")
        self.root.geometry("450x550")

        # --- 변수 초기화 ---
        self.macro_thread = None
        self.stop_event = threading.Event()
        self.windows = {}

        # --- 위젯 생성 ---
        # 1. 창 선택 리스트
        list_frame = tk.Frame(root)
        list_frame.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)
        
        tk.Label(list_frame, text="1. 아래 목록에서 대상 창을 선택하세요.").pack(anchor="w")
        self.scrollbar = tk.Scrollbar(list_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox = tk.Listbox(list_frame, yscrollcommand=self.scrollbar.set, width=60)
        self.listbox.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.scrollbar.config(command=self.listbox.yview)

        # 2. 제어 버튼
        control_frame = tk.Frame(root)
        control_frame.pack(pady=5, padx=10, fill=tk.X)
        
        self.refresh_button = tk.Button(control_frame, text="목록 새로고침", command=self.populate_windows)
        self.refresh_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        tk.Label(root, text="2. 매크로를 시작하거나 중지하세요.").pack(anchor="w", padx=10)
        
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10, padx=10, fill=tk.X)
        
        self.start_button = tk.Button(button_frame, text="매크로 시작", bg="lightgreen", command=self.start_macro)
        self.start_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        self.stop_button = tk.Button(button_frame, text="매크로 중지", bg="lightcoral", command=self.stop_macro, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        # 3. 상태 표시줄
        self.status_label = tk.Label(root, text="상태: 대기 중", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        # --- 초기화 ---
        self.populate_windows()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def populate_windows(self):
        """현재 열린 창 목록으로 리스트박스를 채웁니다."""
        self.listbox.delete(0, tk.END)
        self.windows.clear()
        
        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) != "":
                title = win32gui.GetWindowText(hwnd)
                self.windows[title] = hwnd
                self.listbox.insert(tk.END, title)
        
        win32gui.EnumWindows(callback, None)
        self.status_label.config(text="상태: 목록을 갱신했습니다.")

    def start_macro(self):
        # 1. 창 선택 확인
        selection_indices = self.listbox.curselection()
        if not selection_indices:
            messagebox.showwarning("선택 오류", "먼저 목록에서 창을 선택해주세요.")
            return
        
        # 2. 이미 실행 중인지 확인
        if self.macro_thread and self.macro_thread.is_alive():
            messagebox.showwarning("실행 오류", "매크로가 이미 실행 중입니다.")
            return

        # 3. 선택된 창 정보 가져오기
        selected_title = self.listbox.get(selection_indices[0])
        selected_hwnd = self.windows.get(selected_title)

        if not selected_hwnd:
            messagebox.showerror("오류", "선택된 창을 찾을 수 없습니다. 목록을 새로고침하세요.")
            return

        # 4. 매크로 스레드 시작
        self.stop_event.clear() # 중지 신호 초기화
        self.macro_thread = threading.Thread(
            target=run_macro, 
            args=(selected_hwnd, selected_title, self.stop_event),
            daemon=True  # 메인 프로그램 종료 시 스레드도 함께 종료
        )
        self.macro_thread.start()

        # 5. UI 상태 변경
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text=f"상태: '{selected_title}'에 매크로 실행 중...")

    def stop_macro(self):
        if self.macro_thread and self.macro_thread.is_alive():
            self.stop_event.set() # 중지 신호 보내기
            
        # UI 상태 변경
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="상태: 중지됨.")

    def on_closing(self):
        """GUI 창을 닫을 때 실행되는 함수"""
        if self.macro_thread and self.macro_thread.is_alive():
            self.stop_event.set() # 실행 중인 스레드에 중지 신호
        self.root.destroy()

# --- 메인 실행 부분 ---
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = MacroControlGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"프로그램 실행 중 오류 발생: {e}")