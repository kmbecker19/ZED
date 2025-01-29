from PySide6.QtWidgets import QGridLayout, QLabel, QLineEdit, QVBoxLayout, QComboBox, QDialog, QDialogButtonBox
from PySide6.QtCore import Signal, QTimer
import pyzed.sl as sl


class MessageDialog(QDialog):
    def __init__(self, message: str, title: str=None):
        super().__init__()
        text = message
        self.setWindowTitle(message if title is None else title)
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout = QVBoxLayout()
        message = QLabel(text)
        layout.addWidget(message)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)


class AutoCloseDialog(MessageDialog):
    def __init__(self, message: str, title: str=None, duration: int=3000):
        super().__init__(message, title)
        QTimer.singleShot(duration, self.close)


class ImageSavedDialog(AutoCloseDialog):
    def __init__(self):
        super().__init__("Images Saved")


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
            sl.RESOLUTION.AUTO: "Auto",
            sl.RESOLUTION.VGA: "VGA",
        }
        resolution_label = QLabel("Resolution:")
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["2K", "1080p", "720p", "Auto"])
        self.resolution_combo.setCurrentText(resolution_mapping[init_params.camera_resolution])
        
        # FPS
        fps_label = QLabel("Camera FPS:")
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["15", "30", "60"])
        self.fps_combo.setCurrentText(str(init_params.camera_fps))

        # Depth Mode
        depth_mode_mapping = {
            sl.DEPTH_MODE.ULTRA: "Ultra",
            sl.DEPTH_MODE.PERFORMANCE: "Performance",
            sl.DEPTH_MODE.NEURAL: "Neural",
        }
        depth_mode_label = QLabel("Depth Mode:")
        self.depth_mode_combo = QComboBox()
        self.depth_mode_combo.addItems(["Ultra", "Performance", "Neural"])
        self.depth_mode_combo.setCurrentText(depth_mode_mapping[init_params.depth_mode])

        # Coordinate units
        unit_mapping = {
            sl.UNIT.MILLIMETER: "Millimeters",
            sl.UNIT.CENTIMETER: "Centimeters",
            sl.UNIT.METER: "Meters"
        }
        unit_label = QLabel("Coordinate Units:")
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["Millimeters", "Centimeters", "Meters"])
        self.unit_combo.setCurrentText(unit_mapping[init_params.coordinate_units])

        # Minimum Distance
        min_distance_label = QLabel("Minimum Distance:")
        self.min_distance_box = QLineEdit(f"{init_params.depth_minimum_distance}")

        # Maximum Distance
        max_distance_label = QLabel("Minimum Distance:")
        self.max_distance_box = QLineEdit(f"{init_params.depth_maximum_distance}")

        # Apply Settings Button
        QBtn = QDialogButtonBox.Apply | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.rejected.connect(self.reject)
        apply_button = self.buttonBox.button(QDialogButtonBox.Apply)
        if apply_button:
            apply_button.clicked.connect(self.apply_settings)

        # Layout
        layout = QVBoxLayout()
        main_layout = QGridLayout()
        main_layout.addWidget(resolution_label, 0, 0)
        main_layout.addWidget(self.resolution_combo, 0, 1)
        main_layout.addWidget(fps_label, 1, 0)
        main_layout.addWidget(self.fps_combo, 1, 1)
        main_layout.addWidget(depth_mode_label, 2, 0)
        main_layout.addWidget(self.depth_mode_combo, 2, 1)
        main_layout.addWidget(unit_label, 3, 0)
        main_layout.addWidget(self.unit_combo, 3, 1)
        main_layout.addWidget(min_distance_label, 4, 0)
        main_layout.addWidget(self.min_distance_box, 4, 1)
        main_layout.addWidget(max_distance_label, 5, 0)
        main_layout.addWidget(self.max_distance_box, 5, 1)
        layout.addLayout(main_layout)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def apply_settings(self):
        mappings = {
            "2K": sl.RESOLUTION.HD2K,
            "1080p": sl.RESOLUTION.HD1080,
            "720p": sl.RESOLUTION.HD720,
            "VGA": sl.RESOLUTION.VGA,
            "Auto": sl.RESOLUTION.AUTO,
            "Ultra": sl.DEPTH_MODE.ULTRA,
            "Performance": sl.DEPTH_MODE.PERFORMANCE,
            "Neural": sl.DEPTH_MODE.NEURAL,
            "Millimeters": sl.UNIT.MILLIMETER,
            "Centimeters": sl.UNIT.CENTIMETER,
            "Meters": sl.UNIT.METER
        }
        self.init_params.camera_resolution = mappings[self.resolution_combo.currentText()]
        self.init_params.camera_fps = int(self.fps_combo.currentText())
        self.init_params.depth_mode = mappings[self.depth_mode_combo.currentText()]
        self.init_params.coordinate_units = mappings[self.unit_combo.currentText()]
        self.init_params.depth_minimum_distance = float(self.min_distance_box.text())
        self.init_params.depth_maximum_distance = float(self.max_distance_box.text())
        self.settings_changed.emit(self.init_params)
        dlg = AutoCloseDialog("Camera Settings Updated")
        dlg.exec()
