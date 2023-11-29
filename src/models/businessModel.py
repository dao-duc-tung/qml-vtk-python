from PySide6.QtCore import QObject, Signal
from src.utils import SingletonQObjectMeta


class BusinessModel(QObject, metaclass=SingletonQObjectMeta):
    """
    Cache business data
    """

    sigVisualCylinderChanged = Signal(bool)
    sigRendererColorChanged = Signal(tuple)
    sigPolyDataColorChanged = Signal(tuple)

    def __init__(self):
        super().__init__()

        self.__visualCylinder = False
        self.__rendererColor = [0, 0, 0]
        self.__polyDataColor = [127, 127, 0]

    def getVisualCylinder(self) -> bool:
        return self.__visualCylinder

    def setVisualCylinder(self, val: bool):
        if self.__visualCylinder != val:
            self.__visualCylinder = val
            self.sigVisualCylinderChanged.emit(val)

    def getRendererColor(self) -> bool:
        return self.__rendererColor

    def setRendererColor(self, val: bool):
        if self.__rendererColor != val:
            self.__rendererColor = val
            self.sigRendererColorChanged.emit(val)

    def getPolyDataColor(self) -> bool:
        return self.__polyDataColor

    def setPolyDataColor(self, val: bool):
        if self.__polyDataColor != val:
            self.__polyDataColor = val
            self.sigPolyDataColorChanged.emit(val)
