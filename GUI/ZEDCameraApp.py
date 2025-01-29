import sys
import numpy as np
import pyzed.sl as sl
import cv2
from PySide6.QtWidgets import QApplication, QComboBox, QStatusBar, QFileDialog, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QLineEdit, QToolBar
from PySide6.QtCore import QTimer, Qt, Slot
from PySide6.QtGui import QImage, QPixmap, QAction
from pathlib import Path
from Dialogs import CameraSettingsDialog, ImageSavedDialog

class ZEDCameraApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZED Camera Viewer")
        self.setGeometry(100, 100, 400, 300)

        # Initialize ZED Camera
        self.zed = sl.Camera()
        self.init = sl.InitParameters()
        self.init.camera_resolution = sl.RESOLUTION.HD2K
        self.init.depth_mode = sl.DEPTH_MODE.ULTRA
        self.init.coordinate_units = sl.UNIT.MILLIMETER

        # Open the ZED camera
        if self.zed.open(self.init) != sl.ERROR_CODE.SUCCESS:
            print("Failed to open ZED camera")
            sys.exit(1)

        # Set runtime parameters
        self.runtime_params = sl.RuntimeParameters(enable_fill_mode=True)
        camera_info = self.zed.get_camera_information()
        self.image_size = camera_info.camera_configuration.resolution
        self.image_size.width //= 2
        self.image_size.height //= 2

        # Prepare Mat objects
        self.image_zed = sl.Mat(self.image_size.width, self.image_size.height, sl.MAT_TYPE.U8_C4)
        self.depth_image_zed = sl.Mat(self.image_size.width, self.image_size.height, sl.MAT_TYPE.U8_C4)

        # GUI Elements - Image Display and save button
        self.image_label = QLabel("Camera Feed")
        self.save_image_button = QPushButton("Save Image and Depth Map")
        
        # Menu Bar
        self.setStatusBar(QStatusBar(self))
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        settings_action = QAction("Settings...", self)
        settings_action.triggered.connect(self.open_camera_settings)
        file_menu.addAction(settings_action)
        
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
        self.display_format_combo.addItems(["RGB", "Depth"])
        self.display_format_combo.setCurrentIndex(0)

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
        if self.zed.grab(self.runtime_params) == sl.ERROR_CODE.SUCCESS:
            # Retrieve images
            self.zed.retrieve_image(self.image_zed, sl.VIEW.LEFT, sl.MEM.CPU, self.image_size)
            self.zed.retrieve_image(self.depth_image_zed, sl.VIEW.DEPTH, sl.MEM.CPU, self.image_size)

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

    def open_camera_settings(self):
        # Open camera settings dialog
        dlg = CameraSettingsDialog(self.init)
        dlg.settings_changed.connect(self.update_camera_settings)
        dlg.exec()

    @Slot(sl.InitParameters)
    def update_camera_settings(self, new_params):
        self.init = new_params
        self.zed.close()
        if self.zed.open(self.init) != sl.ERROR_CODE.SUCCESS:
            print("Failed to open ZED camera with updated settings.")
            sys.exit(1)
        print("Camera settings updated.")

    def cv_to_qt(self, cv_image):
        cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGRA2RGBA)
        height, width, channel = cv_image.shape
        bytes_per_line = channel * width
        qt_image = QImage(cv_image.data, width, height, bytes_per_line, QImage.Format_RGBA8888)
        return QPixmap.fromImage(qt_image)

    def save_images(self):
        # Save image and depth map
        image_rgb = self.image_zed.get_data()
        image_depth = self.depth_image_zed.get_data()

        filename_rgb = Path(f"{self.get_filename()}_rgb")
        filename_depth = Path(f"{self.get_filename()}_depth")

        save_folder = Path('../data') / self.folder_text.text() / self.name_text.text()
        if not save_folder.exists():
            save_folder.mkdir(parents=True)

        path_rgb = save_folder / filename_rgb
        path_depth = save_folder / filename_depth

        cv2.imwrite(path_rgb.with_suffix(".png"), image_rgb)
        cv2.imwrite(path_depth.with_suffix(".png"), image_depth)
        np.save(path_depth.with_suffix(".npy"), image_depth)

        self.increment_counter()
        dlg = ImageSavedDialog()
        dlg.exec()

    def save_depth_map(self):
        # Save depth map
        depth_data = self.depth_image_zed.get_data()
        cv2.imwrite("depth_map.png", depth_data)
        print("Depth map saved.")

    def closeEvent(self, event):
        # Cleanup
        self.zed.close()
        event.accept()

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

    def get_filename(self) -> str:
        subject = self.folder_text.text()
        name = self.name_text.text()
        counter = self.counter_text.text().zfill(2)
        return f"{subject}_{name}_{counter}"

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.save_images()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ZEDCameraApp()
    window.show()
    sys.exit(app.exec())
