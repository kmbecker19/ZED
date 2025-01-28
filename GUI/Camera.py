import pyzed.sl as sl

class Camera(object):
    def __init__(self):
        self.__zed = sl.Camera()

        # Set init params
        self.__init_params = sl.InitParameters()
        self.__init_params.sdk_verbose = True
        self.__init_params.depth_mode = sl.DEPTH_MODE.ULTRA
        self.__init_params.coordinate_units = sl.UNIT.MILLLIMETER

        # open the camera
        status = self.__zed.open(self.__init_params)
        if status != sl.ERROR_CODE.SUCCESS:
            raise RuntimeError(f"Error opening the camera: {status}")
        
    def __del__(self):
        self.__zed.close()
        
    @property
    def zed(self):
        return self.__zed
    
    @property
    def init_params(self):
        return self.__init_params

    