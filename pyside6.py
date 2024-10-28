from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QToolBar,
                             QStatusBar)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QFont

class TopNavBar(QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("topNavBar")
        self.setStyleSheet("""
            QToolBar {
                background-color: #1e2124;
                border: none;
                spacing: 5px;
                padding: 5px;
            }
            QPushButton {
                color: #8e9297;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2e3338;
                color: white;
            }
            QPushButton:checked {
                background-color: #393d42;
                color: white;
            }
        """)
        
        # Add navigation items
        nav_items = [
            ("📁 Files", "files"),
            ("☁ Services", "services"),
            ("↑ Uploads", "uploads"),
            ("↓ Downloads", "downloads"),
            (" Help", "help"),
        ]
        
        self.nav_buttons = {}
        for label, name in nav_items:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            self.nav_buttons[name] = btn
            self.addWidget(btn)
            
        # Add settings button aligned to the right
        # self.addStretch()
        settings_btn = QPushButton("⚙ Settings")
        settings_btn.setStyleSheet("""
            QPushButton {
                color: #8e9297;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2e3338;
                color: white;
            }
        """)
        self.addWidget(settings_btn)
        
        # Set Home as initially selected
        self.nav_buttons["files"].setChecked(True)

class FileRow(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("fileRow")
        self.setStyleSheet("""
            #fileRow {
                background-color: #1e2124;
                border-radius: 5px;
                margin: 2px;
                padding: 5px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # File icon and name
        file_icon = QLabel("📄")
        file_name = QLabel("File Name")
        file_name.setStyleSheet("color: white;")
        
        # Upload/Download speeds
        upload_label = QLabel("↑ 0mb/s")
        upload_label.setStyleSheet("color: gray;")
        download_label = QLabel("↓ 0mb/s")
        download_label.setStyleSheet("color: gray;")
        
        # Action buttons
        cancel_btn = QPushButton("×")
        cancel_btn.setStyleSheet("""
            QPushButton {
                color: gray;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                color: white;
            }
        """)
        
        dropbox_btn = QPushButton("☁")
        dropbox_btn.setStyleSheet("""
            QPushButton {
                color: #007ee5;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                color: #0061b0;
            }
        """)
        
        gdrive_btn = QPushButton("☁")
        gdrive_btn.setStyleSheet("""
            QPushButton {
                color: #4285f4;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                color: #3367d6;
            }
        """)
        
        # File size
        size_label = QLabel("999 MB")
        size_label.setStyleSheet("color: gray;")
        
        # Add widgets to layout
        layout.addWidget(file_icon)
        layout.addWidget(file_name, 1)
        layout.addWidget(upload_label)
        layout.addWidget(download_label)
        layout.addWidget(cancel_btn)
        layout.addWidget(dropbox_btn)
        layout.addWidget(gdrive_btn)
        layout.addWidget(size_label)

class MainContent(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)
        
        # Add title
        title = QLabel("Cloud Service Combine")
        title.setStyleSheet("color: white; font-size: 24px; margin-bottom: 20px;")
        self.layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Add file rows
        for _ in range(3):
            self.layout.addWidget(FileRow())
        
        # Add bottom section
        bottom_section = QWidget()
        bottom_layout = QHBoxLayout(bottom_section)
        
        # Add Service section
        service_widget = QWidget()
        service_layout = QVBoxLayout(service_widget)
        service_label = QLabel("Add Service")
        service_label.setStyleSheet("color: white; font-size: 18px;")
        service_layout.addWidget(service_label)
        
        # Service buttons
        service_buttons = QWidget()
        buttons_layout = QHBoxLayout(service_buttons)
        buttons_layout.setSpacing(10)
        
        services = [
            ("Google Drive", "#4285f4"),
            ("Discord", "#7289da"),
            ("Dropbox", "#007ee5")
        ]
        
        for service, color in services:
            btn = QPushButton("☁")
            btn.setStyleSheet(f"""
                QPushButton {{
                    color: {color};
                    border: none;
                    padding: 10px;
                    font-size: 24px;
                }}
                QPushButton:hover {{
                    color: white;
                }}
            """)
            buttons_layout.addWidget(btn)
            
        service_layout.addWidget(service_buttons)
        bottom_layout.addWidget(service_widget)
        
        # Add File section
        add_file_widget = QWidget()
        add_file_layout = QVBoxLayout(add_file_widget)
        add_file_label = QLabel("Add File")
        add_file_label.setStyleSheet("color: white; font-size: 18px;")
        add_file_layout.addWidget(add_file_label)
        
        add_button = QPushButton("+")
        add_button.setStyleSheet("""
            QPushButton {
                color: white;
                border: none;
                padding: 10px;
                font-size: 24px;
            }
            QPushButton:hover {
                color: gray;
            }
        """)
        add_file_layout.addWidget(add_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        bottom_layout.addWidget(add_file_widget)
        self.layout.addWidget(bottom_section)
        
        # Add stretch to push everything up
        self.layout.addStretch()

class CloudServiceCombine(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cloud Service Combine")
        self.setStyleSheet("""
            QMainWindow {
                background-color: #282b30;
            }
        """)
        self.setMinimumSize(1000, 600)
        
        # Add top navigation bar
        self.nav_bar = TopNavBar()
        self.nav_bar.setMovable(False)
        self.addToolBar(self.nav_bar)
        
        # Add status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #1e2124;
                color: #8e9297;
            }
        """)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Add main content
        main_content = MainContent()
        self.setCentralWidget(main_content)

if __name__ == '__main__':
    app = QApplication([])
    window = CloudServiceCombine()
    window.show()
    app.exec()