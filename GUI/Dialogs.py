from PySide6.QtWidgets import QGridLayout, QLabel, QLineEdit, QVBoxLayout, QComboBox, QDialog, QDialogButtonBox, QSlider, QCheckBox
from PySide6.QtCore import Signal, QTimer
import pyzed.sl as sl
from typing import Dict


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
        QBtn = QDialogButtonBox.Apply | QDialogButtonBox.Reset | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.rejected.connect(self.reject)
        apply_button = self.buttonBox.button(QDialogButtonBox.Apply)
        reset_button = self.buttonBox.button(QDialogButtonBox.Reset)
        if apply_button:
            apply_button.clicked.connect(self.apply_settings)
        if reset_button:
            reset_button.clicked.connect(self.reset_params)

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

    def reset_params(self):
        """
        Resets the parameters of the GUI dialog to their default values.

        This method sets the fill mode combo box to its first item, 
        sets the confidence box text to "95", sets the texture confidence 
        box text to "100", and applies these settings.
        """
        self.fill_mode_combo.setCurrentIndex(0)
        self.confidence_box.setText("95")
        self.texture_confidence_box.setText("100")
        self.apply_settings()
        

class VideoSettingsDialog(QDialog):
    """
    A dialog window for adjusting video settings.

    This dialog allows the user to adjust the following video settings:
        - Brightness
        - Contrast
        - Hue
        - Saturation
        - Sharpness
        - Gamma
        - White Balance
        - Gain
        - Exposure

    Attributes:
        settings_changed (Signal): Signal emitted when settings are changed.
        video_settings (Dict[sl.VIDEO_SETTINGS, float]): Dictionary containing the current video settings.

    Methods:
        __init__(video_settings: Dict[sl.VIDEO_SETTINGS, float]):
            Initializes the dialog with the given video settings.
        toggle_auto_white_balance():
            Toggles the state of the white balance slider based on the auto checkbox.
        toggle_auto_gain():
            Toggles the state of the gain slider based on the auto checkbox.
        toggle_auto_exposure():
            Toggles the state of the exposure slider based on the auto checkbox.
        apply_settings():
            Applies the current settings from the sliders and checkboxes to the video settings dictionary and emits the settings_changed signal.
    """
    settings_changed = Signal(Dict[sl.VIDEO_SETTINGS, float])

    def __init__(self, video_settings: Dict[sl.VIDEO_SETTINGS, float]):
        super().__init__()
        self.setWindowTitle("Video Settings")
        self.video_settings = video_settings

        # Brightness
        brightness_label = QLabel("Brightness:")
        self.brightness_slider = QSlider()
        self.brightness_slider.setRange(0, 8)
        self.brightness_slider.setValue(video_settings[sl.VIDEO_SETTINGS.BRIGHTNESS])

        # Contrast
        contrast_label = QLabel("Contrast:")
        self.contrast_slider = QSlider()
        self.contrast_slider.setRange(0, 8)
        self.contrast_slider.setValue(video_settings[sl.VIDEO_SETTINGS.CONTRAST])

        # Hue
        hue_label = QLabel("Hue:")
        self.hue_slider = QSlider()
        self.hue_slider.setRange(0, 11)
        self.hue_slider.setValue(video_settings[sl.VIDEO_SETTINGS.HUE])

        # Saturation
        saturation_label = QLabel("Saturation:")
        self.saturation_slider = QSlider()
        self.saturation_slider.setRange(0, 8)
        self.saturation_slider.setValue(video_settings[sl.VIDEO_SETTINGS.SATURATION])

        # Sharpness
        sharpness_label = QLabel("Sharpness:")
        self.sharpness_slider = QSlider()
        self.sharpness_slider.setRange(0, 8)
        self.sharpness_slider.setValue(video_settings[sl.VIDEO_SETTINGS.SHARPNESS])

        # Gamma
        gamma_label = QLabel("Gamma:")
        self.gamma_slider = QSlider()
        self.gamma_slider.setRange(0, 8)
        self.gamma_slider.setValue(video_settings[sl.VIDEO_SETTINGS.GAMMA])

        # White Balance
        white_balance_label = QLabel("White Balance:")
        self.white_balance_slider = QSlider()
        self.white_balance_slider.setRange(2800, 6500)
        self.white_balance_slider.setValue(video_settings[sl.VIDEO_SETTINGS.WHITEBALANCE])
        self.white_balance_auto_checkbox = QCheckBox("Auto")
        self.white_balance_auto_checkbox.checkStateChanged.connect(self.toggle_auto_white_balance)

        # Gain
        gain_label = QLabel("Gain:")
        self.gain_slider = QSlider()
        self.gain_slider.setRange(0, 100)
        self.gain_slider.setValue(video_settings[sl.VIDEO_SETTINGS.GAIN])
        self.gain_auto_checkbox = QCheckBox("Auto")
        self.gain_auto_checkbox.checkStateChanged.connect(self.toggle_auto_gain)

        # Exposure
        exposure_label = QLabel("Exposure:")
        self.exposure_slider = QSlider()
        self.exposure_slider.setRange(0, 100)
        self.exposure_slider.setValue(video_settings[sl.VIDEO_SETTINGS.EXPOSURE])
        self.exposure_auto_checkbox = QCheckBox("Auto")
        self.exposure_auto_checkbox.checkStateChanged.connect(self.toggle_auto_exposure)

        # Button Box
        QBtn = QDialogButtonBox.Apply | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.rejected.connect(self.reject)
        apply_button = self.buttonBox.button(QDialogButtonBox.Apply)
        if apply_button:
            apply_button.clicked.connect(self.apply_settings)
        
        # Layout
        main_layout = QVBoxLayout()
        layout = QGridLayout()
        layout.addWidget(brightness_label, 0, 0)
        layout.addWidget(self.brightness_slider, 0, 1)
        layout.addWidget(contrast_label, 1, 0)
        layout.addWidget(self.contrast_slider, 1, 1)
        layout.addWidget(hue_label, 2, 0)
        layout.addWidget(self.hue_slider, 2, 1)
        layout.addWidget(saturation_label, 3, 0)
        layout.addWidget(self.saturation_slider, 3, 1)
        layout.addWidget(sharpness_label, 4, 0)
        layout.addWidget(self.sharpness_slider, 4, 1)
        layout.addWidget(gamma_label, 5, 0)
        layout.addWidget(self.gamma_slider, 5, 1)
        layout.addWidget(white_balance_label, 6, 0)
        layout.addWidget(self.white_balance_slider, 6, 1)
        layout.addWidget(self.white_balance_auto_checkbox, 6, 2)
        layout.addWidget(gain_label, 7, 0)
        layout.addWidget(self.gain_slider, 7, 1)
        layout.addWidget(self.gain_auto_checkbox, 7, 2)
        layout.addWidget(exposure_label, 8, 0)
        layout.addWidget(self.exposure_slider, 8, 1)
        layout.addWidget(self.exposure_auto_checkbox, 8, 2)
        main_layout.addLayout(layout)
        main_layout.addWidget(self.buttonBox)
        self.setLayout(main_layout)

    def toggle_auto_white_balance(self):
        """
        Toggles the auto white balance setting.

        This method checks the state of the white balance auto checkbox and 
        enables or disables the white balance slider accordingly. If the 
        auto white balance is enabled, the slider is disabled, and if the 
        auto white balance is disabled, the slider is enabled.
        """
        auto_white_balance = self.white_balance_auto_checkbox.isChecked()
        self.white_balance_slider.setEnabled(not auto_white_balance)

    def toggle_auto_gain(self):
        """
        Toggles the auto gain setting for the gain slider.

        If the auto gain checkbox is checked, the gain slider is disabled.
        If the auto gain checkbox is unchecked, the gain slider is enabled.
        """
        auto_gain = self.gain_auto_checkbox.isChecked()
        self.gain_slider.setEnabled(not auto_gain)
    
    def toggle_auto_exposure(self):
        """
        Toggles the auto exposure setting.

        This method checks the state of the auto exposure checkbox and enables or disables
        the exposure slider accordingly. If auto exposure is enabled, the exposure slider
        is disabled. If auto exposure is disabled, the exposure slider is enabled.
        """
        auto_exposure = self.exposure_auto_checkbox.isChecked()
        self.exposure_slider.setEnabled(not auto_exposure)

    def apply_settings(self):
        """
        Apply the current settings from the sliders and checkboxes to the video settings.

        This method updates the `video_settings` dictionary with the current values from the
        sliders for brightness, contrast, hue, saturation, sharpness, and gamma. It also sets
        the white balance, gain, and exposure settings based on the corresponding sliders and
        checkboxes. If the auto checkbox for white balance, gain, or exposure is checked, the
        setting is set to "Auto".

        Emits:
            settings_changed (dict): Signal emitted with the updated video settings.
        """
        self.video_settings[sl.VIDEO_SETTINGS.BRIGHTNESS] = self.brightness_slider.value()
        self.video_settings[sl.VIDEO_SETTINGS.CONTRAST] = self.contrast_slider.value()
        self.video_settings[sl.VIDEO_SETTINGS.HUE] = self.hue_slider.value()
        self.video_settings[sl.VIDEO_SETTINGS.SATURATION] = self.saturation_slider.value()
        self.video_settings[sl.VIDEO_SETTINGS.SHARPNESS] = self.sharpness_slider.value()
        self.video_settings[sl.VIDEO_SETTINGS.GAMMA] = self.gamma_slider.value()

        # Change these settings to AUTO if the corresponding checkbox is checked
        self.video_settings[sl.VIDEO_SETTINGS.WHITEBALANCE] = self.white_balance_slider.value() \
            if not self.white_balance_auto_checkbox.isChecked() else sl.VIDEO_SETTINGS_VALUE_AUTO
        self.video_settings[sl.VIDEO_SETTINGS.GAIN] = self.gain_slider.value() \
            if not self.gain_auto_checkbox.isChecked() else sl.VIDEO_SETTINGS_VALUE_AUTO
        self.video_settings[sl.VIDEO_SETTINGS.EXPOSURE] = self.exposure_slider.value() \
            if not self.exposure_auto_checkbox.isChecked() else sl.VIDEO_SETTINGS_VALUE_AUTO
        
        self.settings_changed.emit(self.video_settings)

    @staticmethod
    def get_default_settings() -> Dict[sl.VIDEO_SETTINGS, float]:
        """
        Returns a dictionary of video settings with default values.

        Returns:
            Dict[sl.VIDEO_SETTINGS, float]: Dictionary containing default video settings.
        """
        return {
            sl.VIDEO_SETTINGS.BRIGHTNESS: 4,
            sl.VIDEO_SETTINGS.CONTRAST: 4,
            sl.VIDEO_SETTINGS.HUE: 4,
            sl.VIDEO_SETTINGS.SATURATION: 4,
            sl.VIDEO_SETTINGS.SHARPNESS: 4,
            sl.VIDEO_SETTINGS.GAMMA: 4,
            sl.VIDEO_SETTINGS.WHITEBALANCE: sl.VIDEO_SETTINGS_VALUE_AUTO,
            sl.VIDEO_SETTINGS.GAIN: sl.VIDEO_SETTINGS_VALUE_AUTO,
            sl.VIDEO_SETTINGS.EXPOSURE: sl.VIDEO_SETTINGS_VALUE_AUTO
        }

        