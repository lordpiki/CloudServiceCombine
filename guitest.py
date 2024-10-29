import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt6.QtCore import QUrl, QObject, pyqtSlot
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from pathlib import Path

# Bridge class for communication between Python and JavaScript
class WebBridge(QObject):
    @pyqtSlot()
    def uploadFile(self):
        # Open file dialog for uploading files
        file_paths, _ = QFileDialog.getOpenFileNames(None, "Select Files")
        if file_paths:
            for file_path in file_paths:
                print(f"File selected: {file_path}")

        
    @pyqtSlot(str)
    def logMessage(self, message):
        # Log message from JavaScript
        print(f"Message from JavaScript: {message}")
        
    @pyqtSlot(str)
    def downloadFile(self, file_id):
        print(f"Downloading file with ID: {file_id}")
        
    @pyqtSlot(str)
    def deleteFile(self, file_id):
        print(f"Deleting file with ID: {file_id}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize QWebEngineView and WebChannel
        self.web_view = QWebEngineView()
        self.setCentralWidget(self.web_view)
        self.setWindowTitle("HTML with CSS Styling")

        # Set up web channel and bridge
        self.channel = QWebChannel()
        self.bridge = WebBridge()
        self.channel.registerObject("bridge", self.bridge)
        self.web_view.page().setWebChannel(self.channel)

        # Load HTML content from file
        html_file = Path("content.html").resolve().as_uri()
        self.web_view.load(QUrl(html_file))
        
        # Window settings
        self.resize(1600, 900)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
