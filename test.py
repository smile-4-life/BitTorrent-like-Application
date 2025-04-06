import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton

class MiniDownloadApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.downloaded_pieces = 0

    def init_ui(self):
        self.setWindowTitle("Mini Torrent Test")
        self.setGeometry(100, 100, 300, 200)

        self.layout = QVBoxLayout()

        self.status_label = QLabel("Chưa tải mảnh nào.")
        self.layout.addWidget(self.status_label)

        self.download_button = QPushButton("Tải mảnh")
        self.download_button.clicked.connect(self.fake_download_piece)
        self.layout.addWidget(self.download_button)

        self.setLayout(self.layout)

    def fake_download_piece(self):
        self.downloaded_pieces += 1
        self.status_label.setText(f"Đã tải {self.downloaded_pieces} mảnh.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MiniDownloadApp()
    window.show()
    sys.exit(app.exec_())
