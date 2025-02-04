from PySide6.QtWidgets import QGridLayout, QLabel, QLineEdit, QVBoxLayout, QComboBox, QDialog, QDialogButtonBox
from PySide6.QtCore import Signal, QTimer
import pyzed.sl as sl


class MessageDialog(QDialog):
    """
    A dialog window for displaying a message with OK and Cancel buttons.

    Args:
        message (str): The message to be displayed in the dialog.
        title (str, optional): The title of the dialog window. Defaults to None.

    Attributes:
        buttonBox (QDialogButtonBox): The button box containing OK and Cancel buttons.

    Methods:
        accept(): Closes the dialog and sets the result code to Accepted.
        reject(): Closes the dialog and sets the result code to Rejected.
    """
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
    """
    A dialog that automatically closes after a specified duration.

    Args:
        message (str): The message to be displayed in the dialog.
        title (str, optional): The title of the dialog. Defaults to None.
        duration (int, optional): The duration in milliseconds before the dialog closes automatically. Defaults to 3000 ms (3 seconds).
    """
    def __init__(self, message: str, title: str=None, duration: int=3000):
        super().__init__(message, title)
        QTimer.singleShot(duration, self.close)


class ImageSavedDialog(AutoCloseDialog):
    """
    A dialog that indicates images have been saved.

    This dialog automatically closes after a certain period of time.

    Attributes:
        None

    Methods:
        __init__(): Initializes the dialog with a message indicating images have been saved.
    """
    def __init__(self):
        super().__init__("Images Saved")


class CameraSettingsDialog(QDialog):
    """
    A dialog for configuring camera settings. 

    Sends a Signal to the MainWindow of the application to update the ZED depth camera settings
    when the 'Apply' button is clicked.

    Attributes:
        settings_changed (Signal): Signal emitted when settings are changed.
        init_params (sl.InitParameters): Initial parameters for the camera.
        resolution_combo (QComboBox): Combo box for selecting camera resolution.
        fps_combo (QComboBox): Combo box for selecting camera FPS.
        depth_mode_combo (QComboBox): Combo box for selecting depth mode.
        unit_combo (QComboBox): Combo box for selecting coordinate units.
        min_distance_box (QLineEdit): Line edit for setting minimum depth distance.
        max_distance_box (QLineEdit): Line edit for setting maximum depth distance.
        buttonBox (QDialogButtonBox): Dialog button box for applying or canceling changes.
    Methods:
        __init__(init_params: sl.InitParameters): Initializes the dialog with given parameters.
        apply_settings(): Applies the settings and emits the settings_changed signal.
    """
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
        """
        Apply the settings from the GUI to the camera initialization parameters.

        This method retrieves the current selections from the GUI elements (combo boxes and text boxes),
        maps them to the corresponding SDK constants, and updates the camera initialization parameters.
        It then emits a signal indicating that the settings have changed and displays a dialog to inform
        the user that the camera settings have been updated.

        Mappings:
            - Resolution: "2K", "1080p", "720p", "VGA", "Auto"
            - Depth Mode: "Ultra", "Performance", "Neural"
            - Unit: "Millimeters", "Centimeters", "Meters"

        Emits:
            settings_changed: Signal emitted with the updated initialization parameters

        Displays:
            AutoCloseDialog: Dialog indicating that the camera settings have been updated
        """
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


class RunTimeParamDialog(QDialog):
    """
    A dialog for setting runtime parameters.
    Attributes:
        settings_changed (Signal): Signal emitted when settings are changed.
        params (sl.RuntimeParameters): The runtime parameters.
    Methods:
        __init__(params: sl.RuntimeParameters):
            Initializes the dialog with the given runtime parameters.
        apply_settings():
            Applies the settings from the dialog to the runtime parameters and emits the settings_changed signal.
    """

    settings_changed = Signal(sl.RuntimeParameters)

    def __init__(self, params: sl.RuntimeParameters):
        super().__init__()
        self.setWindowTitle("Runtime Parameters")
        self.params = params

        # Fill Mode
        fill_mode_label = QLabel("Fill Mode:")
        self.fill_mode_combo = QComboBox()
        self.fill_mode_combo.addItems(["True", "False"])
        self.fill_mode_combo.setCurrentIndex(0 if params.enable_fill_mode else 1)

        # Confidence Threshold
        confidence_label = QLabel("Confidence Threshold:")
        self.confidence_box = QLineEdit(f"{params.confidence_threshold}")

        # Texture Confidence Threshold
        texture_confidence_label = QLabel("Texture Confidence Threshold:")
        self.texture_confidence_box = QLineEdit(f"{params.texture_confidence_threshold}")

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
        main_layout.addWidget(fill_mode_label, 0, 0)
        main_layout.addWidget(self.fill_mode_combo, 0, 1)
        main_layout.addWidget(confidence_label, 1, 0)
        main_layout.addWidget(self.confidence_box, 1, 1)
        main_layout.addWidget(texture_confidence_label, 2, 0)
        main_layout.addWidget(self.texture_confidence_box, 2, 1)
        layout.addLayout(main_layout)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def apply_settings(self):
        """
        Apply the settings from the GUI to the runtime parameters.

        This method retrieves the current values from the GUI elements, updates the
        runtime parameters accordingly, and emits a signal indicating that the settings
        have changed. It also displays a dialog to inform the user that the runtime
        parameters have been updated.

        Emits:
            settings_changed: Signal emitted with the updated initialization parameters

        Displays:
            AutoCloseDialog: Dialog indicating that the camera settings have been updated
        """
        self.params = sl.RuntimeParameters()
        self.params.enable_fill_mode = self.fill_mode_combo.currentText() == "True"
        self.params.confidence_threshold = float(self.confidence_box.text())
        self.params.texture_confidence_threshold = float(self.texture_confidence_box.text())
        self.settings_changed.emit(self.params)
        dlg = AutoCloseDialog("Runtime Parameters Updated")
        dlg.exec()
        
