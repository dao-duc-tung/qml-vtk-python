from PySide2.QtCore import QObject, QUrl, Signal, Property, Slot
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType, QQmlEngine
from PySide2.QtWidgets import QApplication

from src.ctrls import MainHelper
from src.pieces.graphics import Fbo, ProcessingEngine
from src.utils import get_qml_object

import random


class MainCtrl(QObject):
    sigPosXChanged = Signal(float)
    sigPosYChanged = Signal(float)

    def __init__(self, engine: QQmlApplicationEngine):
        super().__init__()
        self.__engine = engine
        self.__procEngine = ProcessingEngine()

        self.__engine.load(QUrl.fromLocalFile(f":/main.qml"))

        self.__fbo = get_qml_object(self.__engine, "fbo")
        self.__hp = MainHelper(self.__procEngine, self.__fbo)

        self.__posX = 0.0
        self.__posY = 0.0

    def setup(self):
        ctxt = self.__engine.rootContext()
        ctxt.setContextProperty("MainCtrl", self)

        self.__hp.addInteractorStyle()
        self.__hp.addRenderer()
        self.__hp.render()

        self.sigPosXChanged.connect(self.__changeRendererColor)
        self.sigPosYChanged.connect(self.__changeRendererColor)

    def getPosX(self):
        return self.__posX

    def setPosX(self, val: float):
        if self.__posX != val:
            self.__posX = val
            self.sigPosXChanged.emit(val)

    posX = Property(float, fget=getPosX, fset=setPosX, notify=sigPosXChanged)

    def getPosY(self):
        return self.__posY

    def setPosY(self, val: float):
        if self.__posY != val:
            self.__posY = val
            self.sigPosYChanged.emit(val)

    posY = Property(float, fget=getPosY, fset=setPosY, notify=sigPosYChanged)

    @Slot(int, float, float)
    def showPos(self, buttons: int, x: float, y: float):
        self.posX = x
        self.posY = y

    @Slot(str)
    def openModel(self, path):
        qurl = QUrl(path)  # don't use fromLocalFile (it will add file:/// as prefix)
        localFilePath = qurl
        if qurl.isLocalFile():
            # Remove the "file:///" if present
            localFilePath = qurl.toLocalFile()
        self.__hp.toggle_cylinder()
        self.__hp.addMesh(localFilePath)
        self.__hp.updateModelColor()
        self.__hp.focusCamera()
        self.__hp.render()

    @Slot()
    def toggle_cylinder(self):
        self.__hp.toggle_cylinder()
        self.__hp.updateModelColor()
        self.__hp.focusCamera()
        self.__hp.render()

    @Slot(int, int)
    def setModelColor(self, idx: int, val: int):
        self.__hp.model_color[idx] = val
        self.__hp.updateModelColor()
        self.__hp.render()

    def __changeRendererColor(self):
        temp = (self.posX + self.posY) / 2
        new_val = (self.posX, self.posY, temp)
        summ = sum(new_val)
        if summ != 0:
            summ = 1
        self.__hp.renderer_color = [i / (sum(new_val)) for i in new_val]
        self.__hp.updateRendererColor()
        self.__hp.render()
