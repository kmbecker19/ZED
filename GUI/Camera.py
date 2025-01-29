import pyzed.sl as sl
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QImage
import numpy as np

class Camera(QThread):
    frame_grabbed = Signal(QImage)
    def __init__(self):
        super().__init__()
        self.__zed = sl.Camera()

        # Set init params
        self.__init_params = sl.InitParameters()
        self.__init_params.sdk_verbose = 1
        self.__init_params.depth_mode = sl.DEPTH_MODE.ULTRA
        self.__init_params.coordinate_units = sl.UNIT.MILLIMETER

        
    def __del__(self):
        self.__zed.close()
        
    @property
    def zed(self):
        return self.__zed
    
    @property
    def init_params(self):
        return self.__init_params
    
    def run(self):
        # open the camera
        status = self.__zed.open(self.__init_params)
        if status != sl.ERROR_CODE.SUCCESS:
            raise RuntimeError(f"Error opening the camera: {status}")
        
        # Set runtime parameters after opening the camera
        runtime = sl.RuntimeParameters()

        # Prepare new image size to retrieve half-resolution images
        image_size = self.__zed.get_camera_information().camera_configuration.resolution
        image_size.width = image_size.width /2
        image_size.height = image_size.height /2

        # Declare your sl.Mat matrices
        image_zed = sl.Mat(image_size.width, image_size.height, sl.MAT_TYPE.U8_C4)

        # Capture camera feed
        while True:
            status = self.__zed.grab(runtime)
            if status == sl.ERROR_CODE.SUCCESS:
                self.__zed.retrieve_image(image_zed, sl.VIEW.LEFT, sl.MEM.CPU, image_size)
                image_ocv = image_zed.get_data()
                h, w, _ = image_ocv.shape
                qimage = QImage(image_ocv, w, h, 3 * w, QImage.Format_RGBA8888)
                self.frame_grabbed.emit(qimage)

    