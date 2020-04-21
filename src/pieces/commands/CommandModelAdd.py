from PySide2.QtCore import QObject, QUrl, qDebug, qCritical, QFileInfo, QThread, Signal

from ProcessingEngine import ProcessingEngine
from CommandModel import CommandModel
from Model import Model
from QVTKFramebufferObjectRenderer import FboRenderer

class CommandModelAdd(QThread, CommandModel):
    ready = Signal()
    done = Signal()

    def __init__(self, vtkFboRenderer:FboRenderer, processingEngine:ProcessingEngine, modelPath:QUrl):
        super().__init__()
        self.__model:Model = None
        self.__positionX:float = 0.0
        self.__positionY:float = 0.0
        self.__ready:bool = False

        self.__processingEngine:ProcessingEngine = processingEngine
        self.__modelPath:QUrl = modelPath
        self.__vtkFboRenderer:FboRenderer = vtkFboRenderer

    def run(self):
        self.__model = self.__processingEngine.addModel(self.__modelPath)
        self.__processingEngine.placeModel(self.__model)

        self.__ready = True
        self.ready.emit()

    def isReady(self) -> bool:
        return self.__ready

    def execute(self):
        self.__vtkFboRenderer.renderer.addModelActor(self.__model)
        self.done.emit()
