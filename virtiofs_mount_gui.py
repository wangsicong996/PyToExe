import sys
import subprocess
import ctypes
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QTextEdit, QLabel, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont


class MountThread(QThread):
    """后台线程执行挂载操作"""
    finished = pyqtSignal(bool, str, str)  # 成功/失败, VM名称, 消息
    
    def __init__(self, drive_letter, vm_tag):
        super().__init__()
        self.drive_letter = drive_letter
        self.vm_tag = vm_tag
    
    def run(self):
        try:
            virtiofs_path = r"C:\Program Files\Virtio-Win\VioFS\virtiofs.exe"
            cmd = [virtiofs_path, "-d", f"{self.drive_letter}:", "-t", self.vm_tag]
            
            # 直接运行，不需要特殊权限处理
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW  # 不显示命令行窗口
            )
            
            if result.returncode == 0:
                self.finished.emit(True, self.vm_tag, 
                                 f"Successfully mounted {self.drive_letter}: to {self.vm_tag}")
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                self.finished.emit(False, self.vm_tag, 
                                 f"Failed to mount {self.drive_letter}: to {self.vm_tag}\n{error_msg}")
        
        except subprocess.TimeoutExpired:
            self.finished.emit(False, self.vm_tag, f"Mount operation timed out for {self.vm_tag}")
        except FileNotFoundError:
            self.finished.emit(False, self.vm_tag, "virtiofs.exe not found. Please check installation path.")
        except Exception as e:
            self.finished.emit(False, self.vm_tag, f"Error: {str(e)}")


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
    
    def on_mount_finished(self, success, vm_tag, message):
        """挂载操作完成回调"""
        # 恢复按钮
        btn = getattr(self, f"btn_{vm_tag}")
        btn.setEnabled(True)
        drive_letter = self.mount_configs[vm_tag]
        btn.setText(f"Mount {vm_tag} ({drive_letter}:)")
        
        # 记录日志
        if success:
            self.log(f"✓ {message}", "green")
            QMessageBox.information(self, "Success", message)
        else:
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


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用Fusion风格
    
    window = VirtioFSMountGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
