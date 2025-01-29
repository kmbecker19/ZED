import os
import numpy as np
import cv2
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QFileDialog, QVBoxLayout, QWidget, QHBoxLayout, QComboBox, QDialog, QDialogButtonBox, QToolBar, QStatusBar, QSlider
from PySide6.QtGui import QPixmap, QAction, QMouseEvent, QPainter, QPen, QImage
from PySide6.QtCore import Qt, QRect, QPoint, QSize, Slot
from Camera import Camera

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ZED Camera Viewer")
        self.setGeometry(100, 100, 1280, 720)

        # Image naming Toolbar
        # Subject Folder
        self.folder_label = QLabel("Folder: ")
        self.folder_text = QLineEdit("Subject Folder")
        self.folder_text.setReadOnly(True)
        self.folder_button = QPushButton("Choose...")
        self.folder_button.clicked.connect(self.open_folder_dialog)

        # Image Name
        self.name_label = QLabel("Name: ")
        self.name_text = QLineEdit("Image Name")

        # Image Counter
        self.counter_label = QLabel("Counter: ")
        self.counter_text = QLineEdit("1")
        self.counter_text.setReadOnly(True)
        self.counter_minus_button = QPushButton("-")
        self.counter_minus_button.clicked.connect(self.decrement_counter)
        self.counter_plus_button = QPushButton("+")
        self.counter_plus_button.clicked.connect(self.increment_counter)
        self.counter_reset_button = QPushButton("Reset")
        self.counter_reset_button.clicked.connect(self.reset_counter)

        # Image naming layout
        naming_toolbar = QToolBar("ToolBar")
        self.addToolBar(naming_toolbar)
        naming_toolbar.addWidget(self.folder_label)
        naming_toolbar.addWidget(self.folder_text)
        naming_toolbar.addWidget(self.folder_button)
        naming_toolbar.addSeparator()
        naming_toolbar.addWidget(self.name_label)
        naming_toolbar.addWidget(self.name_text)
        naming_toolbar.addSeparator()
        naming_toolbar.addWidget(self.counter_label)
        naming_toolbar.addWidget(self.counter_text)
        naming_toolbar.addWidget(self.counter_minus_button)
        naming_toolbar.addWidget(self.counter_plus_button)
        naming_toolbar.addWidget(self.counter_reset_button)
        
        # Camera Feed Display
        self.display = QLabel(self)
        self.camera = Camera()
        self.camera.frame_grabbed.connect(self.update_display)

        # Application Layout
        layout = QVBoxLayout()
        layout.addWidget(self.display)
        container = QWidget()
        container.setLayout(layout)
        self.setMinimumSize(1024, 1248)
        self.setCentralWidget(container)

        #self.camera.get_feed()

    def open_folder_dialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Subject Folder")
        self.folder_text.setText(Path(folder_path).name)
        
    def increment_counter(self):
        current_counter = int(self.counter_text.text())
        self.counter_text.setText(str(current_counter + 1))

    def decrement_counter(self):
        current_counter = int(self.counter_text.text())
        if current_counter > 1:
            self.counter_text.setText(str(current_counter - 1))

    def reset_counter(self):
        self.counter_text.setText("1")
    
    @Slot(np.ndarray)
    def update_display(self, image_ocv):
        image_cv = cv2.cvtColor(image_ocv, cv2.COLOR_RGBA2BGR)
        image_qt = QImage(image_cv.data, image_cv.shape[1], image_cv.shape[0], QImage.Format_BGR888)
        self.display.setPixmap(QPixmap.fromImage(image_qt))


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()