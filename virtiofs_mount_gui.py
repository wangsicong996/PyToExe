import sys
import subprocess
import ctypes
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QTextEdit, QLabel, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont


class MountThread(QThread):
    """后台线程执行挂载操作"""
    finished = pyqtSignal(bool, str, str, object)  # 成功/失败, VM名称, 消息, 进程对象
    
    def __init__(self, drive_letter, vm_tag):
        super().__init__()
        self.drive_letter = drive_letter
        self.vm_tag = vm_tag
    
    def run(self):
        try:
            virtiofs_path = r"C:\Program Files\Virtio-Win\VioFS\virtiofs.exe"
            cmd = [virtiofs_path, "-d", f"{self.drive_letter}:", "-t", self.vm_tag]
            
            # 启动virtiofs进程，让它持续运行
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW  # 不显示命令行窗口
            )
            
            # 等待一小段时间，检查进程是否启动成功
            import time
            time.sleep(2)
            
            # 检查进程是否还在运行
            if process.poll() is None:
                # 进程还在运行，说明挂载成功
                self.finished.emit(True, self.vm_tag, 
                                 f"Successfully mounted {self.drive_letter}: to {self.vm_tag}\nThe mount will remain active while this application is running.",
                                 process)
            else:
                # 进程已退出，说明失败
                stdout, stderr = process.communicate()
                error_msg = stderr if stderr else stdout
                self.finished.emit(False, self.vm_tag, 
                                 f"Failed to mount {self.drive_letter}: to {self.vm_tag}\n{error_msg}",
                                 None)
        
        except FileNotFoundError:
            self.finished.emit(False, self.vm_tag, "virtiofs.exe not found. Please check installation path.", None)
        except Exception as e:
            self.finished.emit(False, self.vm_tag, f"Error: {str(e)}", None)


class VirtioFSMountGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 挂载配置: {VM标签: 驱动器字母}
        self.mount_configs = {
            "vm888": "X",
            "vm555": "Y",
            "vm666": "J",
            "vm777": "K"
        }
        
        self.mount_threads = {}
        self.mount_processes = {}  # 保存挂载进程，防止被终止
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("VirtioFS Mount Manager")
        self.setGeometry(300, 300, 500, 550)
        
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = QLabel("VirtioFS Mount Manager")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 移除管理员权限警告（不需要了）
        
        # 创建挂载按钮
        for vm_tag in ["vm888", "vm555", "vm666", "vm777"]:
            btn = QPushButton(f"Mount {vm_tag} ({self.mount_configs[vm_tag]}:)")
            btn.setMinimumHeight(50)
            btn.setFont(QFont("Arial", 11))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 5px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:pressed {
                    background-color: #3d8b40;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                    color: #666666;
                }
            """)
            btn.clicked.connect(lambda checked, tag=vm_tag: self.mount_drive(tag))
            layout.addWidget(btn)
            
            # 保存按钮引用
            setattr(self, f"btn_{vm_tag}", btn)
        
        # 日志区域
        log_label = QLabel("Operation Log:")
        log_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        self.log_text.setFont(QFont("Consolas", 9))
        layout.addWidget(self.log_text)
        
        self.log("Application started. Ready to mount drives.")
        if not self.is_admin():
            self.log("Note: Running without administrator privileges. This is usually fine.", "blue")
    
    def is_admin(self):
        """检查是否以管理员权限运行"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def mount_drive(self, vm_tag):
        """挂载指定的虚拟机驱动器"""
        drive_letter = self.mount_configs[vm_tag]
        self.log(f"Starting mount operation for {vm_tag} on {drive_letter}:...")
        
        # 禁用按钮
        btn = getattr(self, f"btn_{vm_tag}")
        btn.setEnabled(False)
        btn.setText(f"Mounting {vm_tag}...")
        
        # 创建并启动挂载线程
        thread = MountThread(drive_letter, vm_tag)
        thread.finished.connect(self.on_mount_finished)
        self.mount_threads[vm_tag] = thread
        thread.start()
    
    def on_mount_finished(self, success, vm_tag, message, process):
        """挂载操作完成回调"""
        # 恢复按钮
        btn = getattr(self, f"btn_{vm_tag}")
        btn.setEnabled(True)
        drive_letter = self.mount_configs[vm_tag]
        
        # 记录日志
        if success:
            # 保存进程引用，防止进程被垃圾回收终止
            self.mount_processes[vm_tag] = process
            
            # 修改按钮文字和颜色，表示已挂载
            btn.setText(f"✓ {vm_tag} Mounted ({drive_letter}:)")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border-radius: 5px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            
            self.log(f"✓ {message}", "green")
            QMessageBox.information(self, "Success", 
                                  f"{message}\n\nKeep this application running to maintain the mount.")
        else:
            btn.setText(f"Mount {vm_tag} ({drive_letter}:)")
            self.log(f"✗ {message}", "red")
            # 检查是否是权限问题
            if "access" in message.lower() or "permission" in message.lower() or "denied" in message.lower():
                reply = QMessageBox.critical(
                    self, 
                    "Permission Error", 
                    f"{message}\n\nThis might require administrator privileges.\nWould you like to restart this application as administrator?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.restart_as_admin()
            else:
                QMessageBox.critical(self, "Error", message)
        
        # 清理线程
        if vm_tag in self.mount_threads:
            del self.mount_threads[vm_tag]
    
    def restart_as_admin(self):
        """以管理员权限重启程序"""
        try:
            if getattr(sys, 'frozen', False):
                # 如果是打包的exe
                exe_path = sys.executable
            else:
                # 如果是python脚本
                exe_path = sys.executable
                params = ' '.join([f'"{arg}"' for arg in sys.argv])
            
            ctypes.windll.shell32.ShellExecuteW(
                None, 
                "runas",  # 以管理员身份运行
                exe_path, 
                params if not getattr(sys, 'frozen', False) else "",
                None, 
                1  # SW_SHOWNORMAL
            )
            QApplication.quit()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to restart as administrator: {str(e)}")
    
    def log(self, message, color="black"):
        """添加日志消息"""
        color_code = {
            "black": "#000000",
            "green": "#008000",
            "red": "#CC0000",
            "blue": "#0000CC"
        }.get(color, "#000000")
        
        self.log_text.append(f'<span style="color: {color_code};">{message}</span>')
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def closeEvent(self, event):
        """程序关闭时清理所有挂载进程"""
        if self.mount_processes:
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                f"There are {len(self.mount_processes)} active mount(s).\nClosing this application will unmount all drives.\n\nAre you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 终止所有挂载进程
                for vm_tag, process in self.mount_processes.items():
                    try:
                        process.terminate()
                        self.log(f"Unmounted {vm_tag}", "blue")
                    except:
                        pass
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用Fusion风格
    
    window = VirtioFSMountGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
