from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QVBoxLayout, QWidget, QHBoxLayout, QComboBox, QDialog, QDialogButtonBox, QToolBar, QStatusBar, QSlider
from PySide6.QtGui import QPixmap, QAction, QMouseEvent, QPainter, QPen
from PySide6.QtCore import Qt, QRect, QPoint, QSize


class MessageDialog(QDialog):
    def __init__(self, message: str):
        super().__init__()
        text = message
        self.setWindowTitle(title)
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout = QVBoxLayout()
        message = QLabel(text)
        layout.addWidget(message)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)


class ImageSavedDialog(MessageDialog):
    def __init__(self):
        super().__init__(f"Image saved!")