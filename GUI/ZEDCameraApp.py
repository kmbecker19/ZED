import sys
import numpy as np
import pyzed.sl as sl
import cv2
import json
from PySide6.QtWidgets import QApplication, QComboBox, QStatusBar, QFileDialog, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QLineEdit, QToolBar
from PySide6.QtCore import QTimer, Qt, Slot
from PySide6.QtGui import QImage, QPixmap, QAction
from pathlib import Path
from Dialogs import CameraSettingsDialog, ImageSavedDialog, RunTimeParamDialog, AutoCloseDialog
from Utils import sobel_filter, param2dict


class ZEDCameraApp(QMainWindow):
    """
    A GUI application for viewing and saving images and depth maps from a ZED camera.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZED Camera Viewer")
        self.setGeometry(100, 100, 400, 300)

        # Path to store the Subject Folder for saving
        self.folder_path: Path

        # Initialize ZED Camera
        self.zed = sl.Camera()
        self.init = sl.InitParameters()
        self.init.camera_resolution = sl.RESOLUTION.HD2K
        self.init.depth_mode = sl.DEPTH_MODE.ULTRA
        self.init.coordinate_units = sl.UNIT.MILLIMETER
        self.init.depth_minimum_distance = 2010
        self.init.depth_maximum_distance = 2520
        
        # Depth estimation turns on positional tracking, set as static
        tracking_params = sl.PositionalTrackingParameters()
        tracking_params.set_as_static = True

        # Open the ZED camera
        if self.zed.open(self.init) != sl.ERROR_CODE.SUCCESS:
            print("Failed to open ZED camera")
            sys.exit(1)

        # Enable Positional tracking (static)
        if self.zed.enable_positional_tracking(tracking_params) != sl.ERROR_CODE.SUCCESS:
            print("Failed to enable positional tracking")
            sys.exit(1)

        # Set runtime parameters
        self.runtime_params = sl.RuntimeParameters(enable_fill_mode=False)
        camera_info = self.zed.get_camera_information()
        self.image_size = camera_info.camera_configuration.resolution
        self.image_size.width //= 2
        self.image_size.height //= 2

        # Prepare Mat objects
        self.image_zed = sl.Mat(self.image_size.width, self.image_size.height, sl.MAT_TYPE.U8_C4)
        self.depth_image_zed = sl.Mat(self.image_size.width, self.image_size.height, sl.MAT_TYPE.U8_C4)
        # For Raw depth data
        self.depth_map_zed = sl.Mat(self.image_size.width, self.image_size.height)

        # GUI Elements - Image Display and save button
        self.image_label = QLabel("Camera Feed")
        self.save_image_button = QPushButton("Save Image and Depth Map")
        self.save_image_button.setFixedHeight(self.save_image_button.sizeHint().height() * 2)
        
        # Menu Bar
        self.setStatusBar(QStatusBar(self))
        menu = self.menuBar()
        settings_menu = menu.addMenu("&Settings")
        # Camera Settings Dialog
        camera_settings_action = QAction("Camera...", self)
        camera_settings_action.triggered.connect(self.open_camera_settings)
        settings_menu.addAction(camera_settings_action)
        # Runtime Params Dialog
        runtime_params_action = QAction("Runtime...", self)
        runtime_params_action.triggered.connect(self.open_runtime_params)
        settings_menu.addAction(runtime_params_action)
        
        # Toolbar
        # Subject Folder
        self.folder_label = QLabel("Folder: ")
        self.folder_text = QLineEdit("Subject Folder")
        self.folder_text.setReadOnly(True)
        self.folder_button = QPushButton("Choose...")
        self.folder_button.clicked.connect(self.open_folder_dialog)
        self.folder_button.setFocusPolicy(Qt.NoFocus)

        # Image Name
        self.name_label = QLabel("Name: ")
        self.name_text = QLineEdit("Image Name")

        # Image Counter
        self.counter_label = QLabel("Counter: ")
        self.counter_text = QLineEdit("1")
        self.counter_text.setReadOnly(True)
        self.counter_minus_button = QPushButton("-")
        self.counter_minus_button.clicked.connect(self.decrement_counter)
        self.counter_minus_button.setFocusPolicy(Qt.NoFocus)
        self.counter_plus_button = QPushButton("+")
        self.counter_plus_button.clicked.connect(self.increment_counter)
        self.counter_plus_button.setFocusPolicy(Qt.NoFocus)
        self.counter_reset_button = QPushButton("Reset")
        self.counter_reset_button.clicked.connect(self.reset_counter)
        self.counter_reset_button.setFocusPolicy(Qt.NoFocus)

        # Display Format

        # Image Display Format
        self.display_format_label = QLabel("Display Format: ")
        self.display_format_combo = QComboBox()
        self.display_format_combo.addItems(["RGB", "Depth", "Sobel"])
        self.display_format_combo.setCurrentIndex(0)
        self.display_format_combo.setFocusPolicy(Qt.NoFocus)

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
        naming_toolbar.addSeparator()
        naming_toolbar.addWidget(self.display_format_label)
        naming_toolbar.addWidget(self.display_format_combo)

        # Connect buttons
        self.save_image_button.clicked.connect(self.save_images)
        self.save_image_button.setAutoDefault(True)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.save_image_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Timer for updating frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frames)
        self.timer.start(1000/60)  # 60fps

    def update_frames(self):
        """
        Updates the frames captured from the ZED camera and displays them in the GUI.

        This method performs the following steps:
        1. Grabs a new frame from the ZED camera.
        2. Retrieves the left view and depth view images from the camera.
        3. Converts the retrieved images to OpenCV format.
        4. Converts the OpenCV images to Qt format.
        5. Displays the converted images in the GUI based on the selected display format.

        The display format can be either "RGB" or "Depth", as selected in the display_format_combo widget.

        Returns:
            None
        """
        if self.zed.grab(self.runtime_params) == sl.ERROR_CODE.SUCCESS:
            # Retrieve images
            self.zed.retrieve_image(self.image_zed, sl.VIEW.LEFT, sl.MEM.CPU, self.image_size)
            self.zed.retrieve_image(self.depth_image_zed, sl.VIEW.DEPTH, sl.MEM.CPU, self.image_size)
            self.zed.retrieve_measure(self.depth_map_zed, sl.MEASURE.DEPTH)
            self.timestamp = self.zed.get_timestamp(sl.TIME_REFERENCE.IMAGE)

            # Convert to OpenCV format
            image_ocv = self.image_zed.get_data()
            depth_ocv = self.depth_image_zed.get_data()

            # Convert to Qt format
            qt_image = self.cv_to_qt(image_ocv)
            qt_depth = self.cv_to_qt(depth_ocv)

            # Display in labels
            if self.display_format_combo.currentText() == "RGB":
                self.image_label.setPixmap(qt_image)
            elif self.display_format_combo.currentText() == "Depth":
                self.image_label.setPixmap(qt_depth)
            elif self.display_format_combo.currentText() == "Sobel":
                sobel_image = sobel_filter(depth_ocv)
                qt_sobel = self.cv_to_qt(sobel_image)
                self.image_label.setPixmap(qt_sobel)

    def open_camera_settings(self):
        """
        Opens the camera settings dialog.

        This method creates an instance of the CameraSettingsDialog, connects the 
        settings_changed signal to the update_camera_settings slot, and executes 
        the dialog to allow the user to change camera settings.
        """
        # Open camera settings dialog
        dlg = CameraSettingsDialog(self.init)
        dlg.settings_changed.connect(self.update_camera_settings)
        dlg.exec()

    @Slot(sl.InitParameters)
    def update_camera_settings(self, new_params):
        """
        Updates the camera settings with the provided parameters.

        This method closes the current ZED camera instance, updates its settings with the
        provided parameters, and attempts to reopen the camera with the new settings. If
        the camera fails to open with the updated settings, the program will exit with an
        error message.

        Args:
            new_params: The new parameters to update the camera settings with.

        Raises:
            SystemExit: If the camera fails to open with the updated settings.
        """
        self.init = new_params
        self.zed.close()
        if self.zed.open(self.init) != sl.ERROR_CODE.SUCCESS:
            print("Failed to open ZED camera with updated settings.")
            sys.exit(1)
        dlg = AutoCloseDialog("Camera Settings Updated")
        dlg.exec()

    def open_runtime_params(self):
        """
        Opens a dialog to modify runtime parameters.

        This method creates an instance of RunTimeParamDialog, passing the current
        runtime parameters to it. It connects the dialog's settings_changed signal
        to the update_runtime_params method to handle any changes made in the dialog.
        Finally, it executes the dialog.
        """
        dlg = RunTimeParamDialog(self.runtime_params)
        dlg.settings_changed.connect(self.update_runtime_params)
        dlg.exec()

    @Slot(sl.RuntimeParameters)
    def update_runtime_params(self, new_params):
        """
        Updates the runtime parameters of the ZED camera application.

        Args:
            new_params (dict): A dictionary containing the new runtime parameters.

        Displays:
            Displays a dialog indicating that the runtime parameters have been updated.
        """
        self.runtime_params = new_params
        dlg = AutoCloseDialog("Runtime Parameters Updated")
        dlg.exec()

    def cv_to_qt(self, cv_image) -> QPixmap:
        """
        Converts an OpenCV image to a QPixmap for use in a Qt application.

        Args:
            cv_image (numpy.ndarray): The OpenCV image to be converted.

        Returns:
            QPixmap: The converted image in QPixmap format.
        """
        cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGRA2RGBA)
        height, width, channel = cv_image.shape
        bytes_per_line = channel * width
        qt_image = QImage(cv_image.data, width, height, bytes_per_line, QImage.Format_RGBA8888)
        return QPixmap.fromImage(qt_image)

    def save_images(self):
        """
        Saves the current RGB image and depth map from the ZED camera to the specified folder.

        This method retrieves the RGB image and depth map from the ZED camera, saves them as PNG files,
        and also saves the depth map as a NumPy array file (.npy). The filenames are generated using
        a predefined naming convention, and the save folder is created if it does not exist.
        """
        # Save image and depth map
        image_rgb = self.image_zed.get_data()
        image_depth = self.depth_image_zed.get_data()
        depth_map = self.depth_map_zed.get_data()

        save_folder = self.get_save_folder()
        if not save_folder.exists():
            save_folder.mkdir(parents=True)

        filename_rgb = Path(f"RGB_{self.get_filename()}")
        filename_depth = Path(f"DEPTH_{self.get_filename()}")

        path_rgb = save_folder / filename_rgb
        path_depth = save_folder / filename_depth

        # Save Image
        cv2.imwrite(path_rgb.with_suffix(".png"), image_rgb)
        cv2.imwrite(path_depth.with_suffix(".png"), image_depth)
        # Save Depth Map
        np.save(path_depth.with_suffix(".npy"), depth_map)
        # Save Metadata
        self.save_metadata(save_folder)

        self.increment_counter()
        dlg = ImageSavedDialog()
        dlg.exec()

    def save_metadata(self, dest: Path):
        """
        Save metadata information to a specified destination.

        This method collects metadata from the image and camera settings,
        and saves it to a file named 'metadata.txt' in the specified destination directory.

        Args:
            dest (Path): The destination directory where the metadata file will be saved.

        Metadata Structure:
            - image_data:
                - name (str): The filename of the image.
                - resolution (str): The resolution of the image in the format "width x height".
                - timestamp (str): The timestamp of the image in milliseconds.
            - init_parameters (dict): The initial camera settings.
            - runtime_parameters (dict): The runtime parameters of the camera.

        Raises:
            IOError: If there is an error writing the metadata file.
        """
        metadata = {}
        metadata["image_data"] = {
            "name" : self.get_filename(),
            "resolution": f"{self.image_zed.get_width()} x {self.image_zed.get_height()}",
            "timestamp": str(self.timestamp.get_milliseconds())
        }
        metadata["init_parameters"] = param2dict(self.init)
        metadata["runtime_parameters"] = param2dict(self.runtime_params)
        # Save Metadata to file
        save_file = dest / "metadata.txt"
        with save_file.open("w") as file:
            json.dump(metadata, file, indent=4)

    def closeEvent(self, event):
        """
        Closes the ZED camera when the application is closed.
        """
        # Cleanup
        self.zed.close()
        event.accept()

    def open_folder_dialog(self):
        """
        Opens a folder dialog for the user to select a directory.

        This method uses QFileDialog to open a dialog window that allows the user to select a directory.
        The selected directory's name is then set to the folder_text widget, and the full path is stored
        in the folder_path attribute.
        """
        folder_path = QFileDialog.getExistingDirectory(self, "Select Subject Folder")
        self.folder_text.setText(Path(folder_path).name)
        self.folder_path = Path(folder_path)

    def increment_counter(self):
        """
        Increments the image counter by 1.
        """
        current_counter = int(self.counter_text.text())
        self.counter_text.setText(str(current_counter + 1))

    def decrement_counter(self):
        """
        Decrements the image counter by 1.
        """
        current_counter = int(self.counter_text.text())
        if current_counter > 1:
            self.counter_text.setText(str(current_counter - 1))

    def reset_counter(self):
        """
        Resets the image counter to 1.
        """
        self.counter_text.setText("1")

    def get_filename(self) -> str:
        """
        Constructs a filename string based on the subject, name, and counter values.
        Returns:
            str: The constructed filename in the format "{subject}_{name}_{counter}".
        """
        subject = self.folder_text.text()
        name = self.name_text.text()
        counter = self.counter_text.text().zfill(2)
        return f"{subject}_{name}_{counter}"

    def get_save_folder(self) -> Path:
        """
        Constructs and returns the path to the save folder.
        The save folder path is constructed using the base folder path (`self.folder_path`),
        the name from the `name_text` widget, and a zero-padded counter from the `counter_text` widget.
        The resulting folder name is in the format: "{name}_{counter}".
        Returns:
            Path: The constructed path to the save folder.
        """
        subj_folder = self.folder_path
        subject = subj_folder.name
        name = self.name_text.text()
        counter = self.counter_text.text().zfill(2)
        folder_name = f"{subject}_{name}_{counter}"
        return subj_folder / folder_name
    
    def keyPressEvent(self, event):
        """
        Saves images if Enter or Return Key is pressed.
        """
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.save_images()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ZEDCameraApp()
    window.show()
    sys.exit(app.exec())
