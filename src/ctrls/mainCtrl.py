import os.path
from pathlib import Path

from PySide6.QtCore import QObject, QUrl, Signal, Property, Slot
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType, QQmlEngine
from PySide6.QtWidgets import QApplication

from src.ctrls import MainHelper
from src.models import BusinessModel
from src.graphics.engines import Fbo, ProcessingEngine
from src.utils import getQmlObject

import random

class MainCtrl(QObject):
    sigPosXChanged = Signal(float)
    sigPosYChanged = Signal(float)

    def __init__(self, engine: QQmlApplicationEngine):
        super().__init__()
        self.__engine = engine
        self.__procEngine = ProcessingEngine()

        self.__posX = 0.0
        self.__posY = 0.0

        ctxt = self.__engine.rootContext()
        ctxt.setContextProperty("MainCtrl", self)

        self.__engine.load(QUrl.fromLocalFile(f":/main.qml"))

        self.__fbo = getQmlObject(self.__engine, "fbo")
        self.__hp = MainHelper(self.__procEngine, self.__fbo)

        self.__businessModel = BusinessModel()

    # * Public
    def setup(self):
        self.__hp.addInteractorStyle()
        self.__hp.addRenderer()
        self.__hp.render()

        self.sigPosXChanged.connect(self.__changeRendererColorInBusinessModel)
        self.sigPosYChanged.connect(self.__changeRendererColorInBusinessModel)

        self.__businessModel.sigVisualCylinderChanged.connect(
            self.__updateCylinderVisibility
        )
        self.__businessModel.sigPolyDataColorChanged.connect(self.__updatePolyDataColor)
        self.__businessModel.sigRendererColorChanged.connect(self.__updateRendererColor)

    # * Property
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

    # * Slot
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

        self.__businessModel.setVisualCylinder(False)
        self.__hp.addMesh(localFilePath)
        self.__hp.updateModelColor(self.__businessModel.getPolyDataColor())
        self.__hp.focusCamera()
        self.__hp.render()

    @Slot()
    def toggleCylinder(self):
        newVal = not self.__businessModel.getVisualCylinder()
        self.__businessModel.setVisualCylinder(newVal)

    @Slot(int, int, int)
    def setModelColor(self, r: int, g: int, b: int):
        newVal = (r, g, b)
        newVal = [i / 255 for i in newVal]
        self.__businessModel.setPolyDataColor(newVal)

    # * Private
    def __changeRendererColorInBusinessModel(self):
        temp = (self.posX + self.posY) / 2
        newVal = (self.posX, self.posY, temp)
        summ = sum(newVal)
        if summ != 0:
            summ = 1
        color = [i / (sum(newVal)) for i in newVal]
        self.__businessModel.setRendererColor(color)

    def __updateCylinderVisibility(self, val: bool):
        self.__hp.updateCylinderVisibility(val)
        if val:
            self.__hp.updateModelColor(self.__businessModel.getPolyDataColor())
        self.__hp.focusCamera()
        self.__hp.render()

    def __updatePolyDataColor(self, color: tuple):
        self.__hp.updateModelColor(color)
        self.__hp.render()

    def __updateRendererColor(self, color: tuple):
        self.__hp.updateRendererColor(color)
        self.__hp.render()
