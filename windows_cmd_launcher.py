#!/usr/bin/env python3
import sys
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout,
                              QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
                              QDialog, QSpinBox, QScrollArea, QFrame, QMessageBox)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QFont, QIcon

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
        font-size: 13px;
        font-weight: 500;
        text-align: center;
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
    }
    QPushButton#settingsButton:hover {
        background-color: #0077ed;
    }
    QScrollArea {
        border: none;
        background-color: #1e1e1e;
    }
    QSpinBox {
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
        {"cmd": "cmd", "name": "命令提示符", "desc": "传统命令行"},
        {"cmd": "powershell", "name": "PowerShell", "desc": "高级命令行"},
        {"cmd": "taskmgr", "name": "任务管理器", "desc": "查看进程"},
        {"cmd": "resmon", "name": "资源监视器", "desc": "资源使用情况"},
        {"cmd": "cleanmgr", "name": "磁盘清理", "desc": "清理临时文件"},
        {"cmd": "dxdiag", "name": "DirectX诊断", "desc": "显卡信息"},
        {"cmd": "mstsc", "name": "远程桌面", "desc": "远程连接"},
    ],
}


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setModal(True)
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.setLayout(layout)
        
        # Button width
        width_layout = QHBoxLayout()
        width_label = QLabel("按钮宽度：")
        self.width_spin = QSpinBox()
        self.width_spin.setRange(80, 300)
        self.width_spin.setValue(parent.settings.value("button_width", 150, int))
        width_layout.addWidget(width_label)
        width_layout.addWidget(self.width_spin)
        width_layout.addStretch()
        layout.addLayout(width_layout)
        
        # Button height
        height_layout = QHBoxLayout()
        height_label = QLabel("按钮高度：")
        self.height_spin = QSpinBox()
        self.height_spin.setRange(40, 200)
        self.height_spin.setValue(parent.settings.value("button_height", 80, int))
        height_layout.addWidget(height_label)
        height_layout.addWidget(self.height_spin)
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
        self.columns_spin.setRange(2, 10)
        self.columns_spin.setValue(parent.settings.value("grid_columns", 4, int))
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
        self.setWindowTitle("Windows 命令快捷启动器")
        self.resize(1000, 700)
        
        # Settings
        self.settings = QSettings("WindowsCmdLauncher", "Config")
        
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
    
    def build_command_grid(self):
        # Clear existing widgets
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Get settings
        button_width = self.settings.value("button_width", 150, int)
        button_height = self.settings.value("button_height", 80, int)
        border_radius = self.settings.value("border_radius", 8, int)
        grid_columns = self.settings.value("grid_columns", 4, int)
        
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
                
                button = QPushButton(cmd_info["name"])
                button.setFixedSize(button_width, button_height)
                button.setToolTip(f"{cmd_info['desc']}\n命令: {cmd_info['cmd']}")
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #2d2d2d;
                        color: #e0e0e0;
                        border: 1px solid #3d3d3d;
                        border-radius: {border_radius}px;
                        font-size: 13px;
                        font-weight: 500;
                        padding: 5px;
                    }}
                    QPushButton:hover {{
                        background-color: #3d3d3d;
                        border: 1px solid #0a84ff;
                    }}
                    QPushButton:pressed {{
                        background-color: #4d4d4d;
                    }}
                """)
                button.clicked.connect(lambda checked, cmd=cmd_info["cmd"]: self.run_command(cmd))
                
                grid_layout.addWidget(button, row, col)
            
            self.content_layout.addLayout(grid_layout)
        
        self.content_layout.addStretch()
    
    def run_command(self, command):
        try:
            # Try to run the command
            subprocess.Popen(command, shell=True)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法运行命令：{command}\n\n错误：{str(e)}")
    
    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec_():
            # Save settings
            self.settings.setValue("button_width", dialog.width_spin.value())
            self.settings.setValue("button_height", dialog.height_spin.value())
            self.settings.setValue("border_radius", dialog.radius_spin.value())
            self.settings.setValue("grid_columns", dialog.columns_spin.value())
            
            # Rebuild grid
            self.build_command_grid()
            
            QMessageBox.information(self, "设置已保存", "设置已保存并应用！")


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(MACOS_DARK_STYLE)
    
    window = CommandLauncher()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
, command):
        try:
            # Try to run the command
            subprocess.Popen(command, shell=True)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法运行命令：{command}\n\n错误：{str(e)}")
    
    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            # Save settings
            self.settings.setValue("button_width", dialog.width_spin.value())
            self.settings.setValue("button_height", dialog.height_spin.value())
            self.settings.setValue("border_radius", dialog.radius_spin.value())
            self.settings.setValue("grid_columns", dialog.columns_spin.value())
            
            # Rebuild grid
            self.build_command_grid()
            
            QMessageBox.information(self, "设置已保存", "设置已保存并应用！")


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(MACOS_DARK_STYLE)
    
    window = CommandLauncher()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
