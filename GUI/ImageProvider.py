from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtGui import QIcon, QPixmap, QImage
from PySide6.QtWidgets import QFileDialog, QApplication
from PySide6.QtCore import Qt, QThread, Signal, Slot, QObject, QSize
from PySide6.QtQuick import QQuickPaintedItem, QQuickView, QQuickImageProvider

import numpy as np
from Camera import Camera

class ImageProvider(QQuickImageProvider):
    imageChanged = Signal(QImage)

    def __init__(self):
        super(ImageProvider, self).__init__(QQuickImageProvider.Image)

        self.cam = Camera() 
        self.cam.frame_grabbed.connect(self.update_image)
        self.image = None

    def requestImage(self, id, size, requestedSize):
        if self.image:
            img = self.image
        else:
            img = QImage(600, 500, QImage.Format_RGBA8888)
            img.fill(Qt.black)

        return img
          
    @Slot(np.ndarray)
    def update_image(self, img):
        self.imageChanged.emit(img)
        self.image = img
    
    @Slot()
    def start(self):
        print("Starting...")
        self.cam.start()
    
    @Slot()
    def killThread(self):
        print("Finishing...")
        try:
            self.cam.close()
        except:
            pass
