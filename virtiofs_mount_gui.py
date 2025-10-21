#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import subprocess
import os
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout,
                              QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
                              QDialog, QSpinBox, QScrollArea, QMessageBox,
                              QLineEdit, QTextEdit, QFrame)
from PyQt5.QtCore import Qt, QSettings, QByteArray, QMimeData
from PyQt5.QtGui import QFont, QPixmap, QImage

# macOS Dark 样式
MACOS_DARK_STYLE = """
    QMainWindow, QDialog, QWidget {
        background-color: #1e1e1e;
        color: #e0e0e0;
    }
    QLabel {
        color: #e0e0e0;
        font-size: 13px;
    }
    QPushButton {
        background-color: #2d2d2d;
        color: #e0e0e0;
        border: 1px solid #3d3d3d;
        text-align: left;
        padding: 5px;
    }
    QPushButton:hover {
        background-color: #3d3d3d;
        border: 1px solid #0a84ff;
    }
    QPushButton:pressed {
        background-color: #4d4d4d;
    }
    QPushButton#settingsButton {
        background-color: #0a84ff;
        border: none;
        text-align: center;
    }
    QPushButton#settingsButton:hover {
        background-color: #0077ed;
    }
    QScrollArea {
        border: none;
        background-color: #1e1e1e;
    }
    QSpinBox, QLineEdit, QTextEdit {
        background-color: #2d2d2d;
        color: #e0e0e0;
        border: 1px solid #3d3d3d;
        border-radius: 6px;
        padding: 6px;
    }
    QDialog QPushButton {
        background-color: #0a84ff;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        text-align: center;
    }
    QDialog QPushButton:hover {
        background-color: #0077ed;
    }
    QDialog QPushButton#cancelButton {
        background-color: #3d3d3d;
    }
    QDialog QPushButton#cancelButton:hover {
        background-color: #4d4d4d;
    }
"""

# Windows命令列表
COMMANDS = {
    "系统管理": [
        {"cmd": "compmgmt.msc", "name": "计算机管理", "desc": "综合管理工具"},
        {"cmd": "devmgmt.msc", "name": "设备管理器", "desc": "管理硬件设备"},
        {"cmd": "diskmgmt.msc", "name": "磁盘管理", "desc": "分区和格式化"},
        {"cmd": "eventvwr.msc", "name": "事件查看器", "desc": "查看系统日志"},
        {"cmd": "perfmon.msc", "name": "性能监视器", "desc": "监控系统性能"},
        {"cmd": "taskschd.msc", "name": "任务计划程序", "desc": "管理计划任务"},
        {"cmd": "services.msc", "name": "服务管理", "desc": "管理系统服务"},
        {"cmd": "msconfig", "name": "系统配置", "desc": "启动项配置"},
        {"cmd": "msinfo32", "name": "系统信息", "desc": "查看系统信息"},
    ],
    "网络管理": [
        {"cmd": "ncpa.cpl", "name": "网络连接", "desc": "禁用/启用网卡"},
        {"cmd": "firewall.cpl", "name": "防火墙", "desc": "基本防火墙设置"},
        {"cmd": "wf.msc", "name": "高级防火墙", "desc": "详细防火墙规则"},
        {"cmd": "inetcpl.cpl", "name": "Internet选项", "desc": "浏览器设置"},
    ],
    "用户和安全": [
        {"cmd": "lusrmgr.msc", "name": "用户和组", "desc": "管理用户账户"},
        {"cmd": "secpol.msc", "name": "安全策略", "desc": "密码策略等"},
        {"cmd": "certmgr.msc", "name": "证书管理", "desc": "管理数字证书"},
        {"cmd": "netplwiz", "name": "用户账户", "desc": "简化用户管理"},
    ],
    "组策略": [
        {"cmd": "gpedit.msc", "name": "组策略编辑器", "desc": "高级系统配置"},
        {"cmd": "rsop.msc", "name": "策略结果集", "desc": "查看应用策略"},
    ],
    "控制面板": [
        {"cmd": "control", "name": "控制面板", "desc": "主控制面板"},
        {"cmd": "appwiz.cpl", "name": "程序和功能", "desc": "卸载程序"},
        {"cmd": "sysdm.cpl", "name": "系统属性", "desc": "计算机名等"},
        {"cmd": "powercfg.cpl", "name": "电源选项", "desc": "电源计划设置"},
        {"cmd": "timedate.cpl", "name": "日期和时间", "desc": "时间设置"},
        {"cmd": "main.cpl", "name": "鼠标属性", "desc": "鼠标设置"},
        {"cmd": "desk.cpl", "name": "显示设置", "desc": "屏幕分辨率"},
        {"cmd": "mmsys.cpl", "name": "声音", "desc": "音频设备设置"},
    ],
    "其他工具": [
        {"cmd": "regedit", "name": "注册表编辑器", "desc": "编辑注册表"},
        {"cmd": "cmd", "name": "命令提示符", "desc": "传统命令行", "special": "cmd"},
        {"cmd": "powershell", "name": "PowerShell", "desc": "高级命令行", "special": "powershell"},
        {"cmd": "cmd_admin", "name": "CMD(管理员)", "desc": "管理员权限CMD", "special": "cmd_admin"},
        {"cmd": "powershell_admin", "name": "PS(管理员)", "desc": "管理员权限PS", "special": "powershell_admin"},
        {"cmd": "taskmgr", "name": "任务管理器", "desc": "查看进程"},
        {"cmd": "resmon", "name": "资源监视器", "desc": "资源使用情况"},
        {"cmd": "cleanmgr", "name": "磁盘清理", "desc": "清理临时文件"},
        {"cmd": "dxdiag", "name": "DirectX诊断", "desc": "显卡信息"},
        {"cmd": "mstsc", "name": "远程桌面", "desc": "远程连接"},
    ],
}


class ImageDropArea(QLabel):
    """可以接收拖放和剪贴板的图片区域"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(200, 200)
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #0a84ff;
                border-radius: 8px;
                background-color: #2d2d2d;
                color: #808080;
            }
        """)
        self.setText("点击获取剪贴板图片\n或拖入图片文件")
        self.pixmap_data = None
        
    def mousePressEvent(self, event):
        """点击获取剪贴板图片"""
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        
        if mime_data.hasImage():
            image = clipboard.image()
            if not image.isNull():
                pixmap = QPixmap.fromImage(image)
                self.set_image(pixmap)
        else:
            QMessageBox.information(self, "提示", "剪贴板中没有图片")
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() or event.mimeData().hasImage():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            file_path = url.toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    self.set_image(pixmap)
        elif event.mimeData().hasImage():
            image = event.mimeData().imageData()
            pixmap = QPixmap.fromImage(image)
            self.set_image(pixmap)
    
    def set_image(self, pixmap):
        """设置并缩放图片"""
        scaled = pixmap.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(scaled)
        # 保存原始数据
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QBuffer.WriteOnly)
        pixmap.save(buffer, "PNG")
        self.pixmap_data = byte_array.toBase64().data().decode()
    
    def get_image_data(self):
        """获取图片的base64数据"""
        return self.pixmap_data


from PyQt5.QtCore import QBuffer


class NoteDialog(QDialog):
    """备注和图片编辑对话框"""
    def __init__(self, cmd_info, current_note="", current_image=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"编辑备注 - {cmd_info['name']}")
        self.setModal(True)
        self.setFixedSize(500, 500)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.setLayout(layout)
        
        # 备注输入
        note_label = QLabel("备注：")
        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText("输入备注信息...")
        self.note_input.setMaximumHeight(100)
        self.note_input.setText(current_note)
        
        layout.addWidget(note_label)
        layout.addWidget(self.note_input)
        
        # 图片区域
        image_label = QLabel("缩略图：")
        self.image_area = ImageDropArea()
        
        # 如果有现有图片，显示它
        if current_image:
            try:
                byte_array = QByteArray.fromBase64(current_image.encode())
                pixmap = QPixmap()
                pixmap.loadFromData(byte_array)
                self.image_area.setPixmap(pixmap.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.image_area.pixmap_data = current_image
            except:
                pass
        
        layout.addWidget(image_label)
        layout.addWidget(self.image_area)
        
        # 按钮
        button_layout = QHBoxLayout()
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.accept)
        clear_image_button = QPushButton("清除图片")
        clear_image_button.setObjectName("cancelButton")
        clear_image_button.clicked.connect(self.clear_image)
        cancel_button = QPushButton("取消")
        cancel_button.setObjectName("cancelButton")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(clear_image_button)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        layout.addLayout(button_layout)
    
    def clear_image(self):
        """清除图片"""
        self.image_area.clear()
        self.image_area.setText("点击获取剪贴板图片\n或拖入图片文件")
        self.image_area.pixmap_data = None
    
    def get_note(self):
        return self.note_input.toPlainText()
    
    def get_image(self):
        return self.image_area.get_image_data()


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setModal(True)
        self.setFixedSize(450, 400)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.setLayout(layout)
        
        # Window size
        size_label = QLabel("窗口大小：")
        size_layout = QHBoxLayout()
        width_label = QLabel("宽度：")
        self.width_spin = QSpinBox()
        self.width_spin.setRange(800, 3000)
        self.width_spin.setValue(parent.settings.value("window_width", 1750, int))
        height_label = QLabel("高度：")
        self.height_spin = QSpinBox()
        self.height_spin.setRange(600, 2000)
        self.height_spin.setValue(parent.settings.value("window_height", 750, int))
        size_layout.addWidget(width_label)
        size_layout.addWidget(self.width_spin)
        size_layout.addWidget(height_label)
        size_layout.addWidget(self.height_spin)
        size_layout.addStretch()
        layout.addWidget(size_label)
        layout.addLayout(size_layout)
        
        # Button height
        height_layout = QHBoxLayout()
        height_label = QLabel("按钮高度：")
        self.button_height_spin = QSpinBox()
        self.button_height_spin.setRange(60, 200)
        self.button_height_spin.setValue(parent.settings.value("button_height", 100, int))
        height_layout.addWidget(height_label)
        height_layout.addWidget(self.button_height_spin)
        height_layout.addStretch()
        layout.addLayout(height_layout)
        
        # Border radius
        radius_layout = QHBoxLayout()
        radius_label = QLabel("圆角大小：")
        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(0, 30)
        self.radius_spin.setValue(parent.settings.value("border_radius", 8, int))
        radius_layout.addWidget(radius_label)
        radius_layout.addWidget(self.radius_spin)
        radius_layout.addStretch()
        layout.addLayout(radius_layout)
        
        # Grid columns
        columns_layout = QHBoxLayout()
        columns_label = QLabel("每行列数：")
        self.columns_spin = QSpinBox()
        self.columns_spin.setRange(2, 15)
        self.columns_spin.setValue(parent.settings.value("grid_columns", 10, int))
        columns_layout.addWidget(columns_label)
        columns_layout.addWidget(self.columns_spin)
        columns_layout.addStretch()
        layout.addLayout(columns_layout)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("取消")
        cancel_button.setObjectName("cancelButton")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        layout.addLayout(button_layout)


class CommandLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Settings
        self.settings = QSettings("WindowsCmdLauncher", "Config")
        
        # Load custom data (notes and images)
        self.load_custom_data()
        
        # Initialize window
        width = self.settings.value("window_width", 1750, int)
        height = self.settings.value("window_height", 750, int)
        self.setWindowTitle("Windows 命令快捷启动器")
        self.resize(width, height)
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        main_widget.setLayout(main_layout)
        
        # Title bar
        title_layout = QHBoxLayout()
        title_label = QLabel("Windows 命令快捷启动器")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        settings_button = QPushButton("⚙ 设置")
        settings_button.setObjectName("settingsButton")
        settings_button.setFixedSize(100, 35)
        settings_button.clicked.connect(self.open_settings)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(settings_button)
        main_layout.addLayout(title_layout)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.content_layout.setSpacing(20)
        self.content_widget.setLayout(self.content_layout)
        
        scroll.setWidget(self.content_widget)
        main_layout.addWidget(scroll)
        
        # Build UI
        self.build_command_grid()
    
    def load_custom_data(self):
        """加载自定义数据（备注和图片）"""
        try:
            data_file = os.path.join(os.path.expanduser("~"), ".windows_cmd_launcher_data.json")
            if os.path.exists(data_file):
                with open(data_file, 'r', encoding='utf-8') as f:
                    self.custom_data = json.load(f)
            else:
                self.custom_data = {}
        except:
            self.custom_data = {}
    
    def save_custom_data(self):
        """保存自定义数据"""
        try:
            data_file = os.path.join(os.path.expanduser("~"), ".windows_cmd_launcher_data.json")
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(self.custom_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存数据失败：{str(e)}")
    
    def build_command_grid(self):
        # Clear existing widgets
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Get settings
        button_height = self.settings.value("button_height", 100, int)
        border_radius = self.settings.value("border_radius", 8, int)
        grid_columns = self.settings.value("grid_columns", 10, int)
        
        # Build sections
        for category, commands in COMMANDS.items():
            # Category label
            category_label = QLabel(category)
            category_label.setFont(QFont("Arial", 14, QFont.Bold))
            category_label.setStyleSheet("color: #0a84ff; margin-top: 10px;")
            self.content_layout.addWidget(category_label)
            
            # Grid layout for buttons
            grid_layout = QGridLayout()
            grid_layout.setSpacing(10)
            grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            
            for idx, cmd_info in enumerate(commands):
                row = idx // grid_columns
                col = idx % grid_columns
                
                # Create button
                button = QPushButton()
                button.setFixedHeight(button_height)
                button.setMinimumWidth(button_height)  # 至少是正方形
                button.setContextMenuPolicy(Qt.CustomContextMenu)
                button.customContextMenuRequested.connect(
                    lambda pos, info=cmd_info: self.show_button_context_menu(pos, info)
                )
                
                # Button layout: 左侧图片，右侧文字
                btn_layout = QHBoxLayout()
                btn_layout.setContentsMargins(5, 5, 5, 5)
                btn_layout.setSpacing(8)
                
                # 左侧：图片区域（正方形）
                image_label = QLabel()
                image_size = button_height - 10
                image_label.setFixedSize(image_size, image_size)
                image_label.setStyleSheet("background-color: #1e1e1e; border-radius: 4px;")
                image_label.setAlignment(Qt.AlignCenter)
                
                # 加载自定义图片
                cmd_key = cmd_info["cmd"]
                if cmd_key in self.custom_data and "image" in self.custom_data[cmd_key]:
                    try:
                        image_data = self.custom_data[cmd_key]["image"]
                        byte_array = QByteArray.fromBase64(image_data.encode())
                        pixmap = QPixmap()
                        pixmap.loadFromData(byte_array)
                        scaled = pixmap.scaled(image_size-10, image_size-10, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        image_label.setPixmap(scaled)
                    except:
                        image_label.setText("📁")
                        image_label.setStyleSheet("background-color: #1e1e1e; border-radius: 4px; font-size: 32px;")
                else:
                    image_label.setText("📁")
                    image_label.setStyleSheet("background-color: #1e1e1e; border-radius: 4px; font-size: 32px;")
                
                # 右侧：文字区域
                text_layout = QVBoxLayout()
                text_layout.setSpacing(2)
                text_layout.setContentsMargins(0, 0, 0, 0)
                
                # 名称
                name_label = QLabel(cmd_info["name"])
                name_label.setStyleSheet("color: #e0e0e0; font-size: 13px; font-weight: bold; background: transparent;")
                name_label.setWordWrap(True)
                
                # 说明
                desc_label = QLabel(cmd_info["desc"])
                desc_label.setStyleSheet("color: #d4b975; font-size: 10px; background: transparent;")  # 黄色
                desc_label.setWordWrap(True)
                
                # 备注
                note_label = QLabel()
                note_label.setStyleSheet("color: #808080; font-size: 9px; font-style: italic; background: transparent;")
                note_label.setWordWrap(True)
                if cmd_key in self.custom_data and "note" in self.custom_data[cmd_key]:
                    note_label.setText(self.custom_data[cmd_key]["note"])
                
                text_layout.addWidget(name_label)
                text_layout.addWidget(desc_label)
                if note_label.text():
                    text_layout.addWidget(note_label)
                text_layout.addStretch()
                
                btn_layout.addWidget(image_label)
                btn_layout.addLayout(text_layout, 1)
                
                button.setLayout(btn_layout)
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #2d2d2d;
                        border: 1px solid #3d3d3d;
                        border-radius: {border_radius}px;
                    }}
                    QPushButton:hover {{
                        background-color: #3d3d3d;
                        border: 1px solid #0a84ff;
                    }}
                    QPushButton:pressed {{
                        background-color: #4d4d4d;
                    }}
                """)
                
                button.clicked.connect(lambda checked, info=cmd_info: self.run_command(info))
                
                grid_layout.addWidget(button, row, col)
            
            self.content_layout.addLayout(grid_layout)
        
        self.content_layout.addStretch()
    
    def show_button_context_menu(self, pos, cmd_info):
        """显示按钮右键菜单"""
        from PyQt5.QtWidgets import QMenu
        menu = QMenu(self)
        edit_action = menu.addAction("编辑备注和图片")
        
        action = menu.exec_(self.sender().mapToGlobal(pos))
        if action == edit_action:
            self.edit_button_note(cmd_info)
    
    def edit_button_note(self, cmd_info):
        """编辑按钮备注和图片"""
        cmd_key = cmd_info["cmd"]
        current_note = ""
        current_image = None
        
        if cmd_key in self.custom_data:
            current_note = self.custom_data[cmd_key].get("note", "")
            current_image = self.custom_data[cmd_key].get("image", None)
        
        dialog = NoteDialog(cmd_info, current_note, current_image, self)
        if dialog.exec_():
            note = dialog.get_note()
            image = dialog.get_image()
            
            if cmd_key not in self.custom_data:
                self.custom_data[cmd_key] = {}
            
            self.custom_data[cmd_key]["note"] = note
            self.custom_data[cmd_key]["image"] = image
            
            self.save_custom_data()
            self.build_command_grid()
    
    def run_command(self, cmd_info):
        try:
            command = cmd_info["cmd"]
            special = cmd_info.get("special", None)
            
            if special == "cmd":
                subprocess.Popen(["cmd.exe", "/k"], creationflags=subprocess.CREATE_NEW_CONSOLE)
            elif special == "powershell":
                subprocess.Popen(["powershell.exe", "-NoExit"], creationflags=subprocess.CREATE_NEW_CONSOLE)
            elif special == "cmd_admin":
                import ctypes
                ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", "/k", None, 1)
            elif special == "powershell_admin":
                import ctypes
                ctypes.windll.shell32.ShellExecuteW(None, "runas", "powershell.exe", "-NoExit", None, 1)
            else:
                subprocess.Popen(command, shell=True)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法运行命令：{cmd_info['name']}\n\n错误：{str(e)}")
    
    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec_():
            self.settings.setValue("window_width", dialog.width_spin.value())
            self.settings.setValue("window_height", dialog.height_spin.value())
            self.settings.setValue("button_height", dialog.button_height_spin.value())
            self.settings.setValue("border_radius", dialog.radius_spin.value())
            self.settings.setValue("grid_columns", dialog.columns_spin.value())
            
            self.build_command_grid()
            
            QMessageBox.information(self, "设置已保存", "设置已保存并应用！\n重启应用以应用窗口大小。")
    
    def closeEvent(self, event):
        # Save current window size
        self.settings.setValue("window_width", self.width())
        self.settings.setValue("window_height", self.height())
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(MACOS_DARK_STYLE)
    
    window = CommandLauncher()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
