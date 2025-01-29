from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QVBoxLayout, QWidget, QHBoxLayout, QComboBox, QDialog, QDialogButtonBox, QToolBar, QStatusBar, QSlider
from PySide6.QtGui import QPixmap, QAction, QMouseEvent, QPainter, QPen
from PySide6.QtCore import Qt, QRect, QPoint, QSize, Signal
import pyzed.sl as sl

class MessageDialog(QDialog):
    def __init__(self, title: str, message: str):
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
        super().__init__("Image Saved", f"Image saved!")


class CameraSettingsDialog(QDialog):
    # Signal
    settings_changed = Signal(sl.InitParameters)
    def __init__(self, init_params: sl.InitParameters):
        super().__init__()
        self.setWindowTitle("Camera Settings")
        self.init_params = init_params

        # Resolution
        resolution_mapping = {
            sl.RESOLUTION.HD2K: "2K",
            sl.RESOLUTION.HD1080: "1080p",
            sl.RESOLUTION.HD720: "720p",
            sl.RESOLUTION.VGA: "VGA"
        }
        resolution_label = QLabel("Resolution:")
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["2K", "1080p", "720p", "VGA"])
        self.resolution_combo.setCurrentText(resolution_mapping[init_params.camera_resolution])
        
        # FPS

        # Depth Mode

        # Coordinate units

        # Minimum Distance

        # Maximum Distance


'''
        # Resolution
        resolution_label = QLabel("Resolution:")
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["2K", "1080p", "720p", "VGA"])
        self.resolution_combo.setCurrentIndex(self.resolution_combo.findText(self.init_params.camera_resolution.name()))

        # Depth mode
        depth_mode_label = QLabel("Depth Mode:")
        self.depth_mode_combo = QComboBox()
        self.depth_mode_combo.addItems(["Ultra", "Medium", "Low", "Night"])
        self.depth_mode_combo.setCurrentIndex(self.depth_mode_combo.findText(self.init_params.depth_mode.name()))

        # Coordinate units
'''
