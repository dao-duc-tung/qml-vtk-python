from PySide2.QtCore import QObject, QUrl, qDebug, qCritical, QFileInfo, QThread, Signal

from ProcessingEngine import ProcessingEngine
from CommandModel import CommandModel
from Model import Model
from QVTKFramebufferObjectRenderer import SquircleInFboRenderer

class CommandModelAddConnection(QObject):
    ready = Signal()
    done = Signal()

class CommandModelAdd(QThread, CommandModel):
    def __init__(self, vtkFboRenderer:SquircleInFboRenderer, processingEngine:ProcessingEngine, modelPath:QUrl):
        super().__init__()
        self.signal_conn = CommandModelAddConnection()
        self.__m_model:Model = None
        self.__m_positionX:float = 0.0
        self.__m_positionY:float = 0.0
        self.__m_ready:bool = False

        self.__m_processingEngine:ProcessingEngine = processingEngine
        self.__m_modelPath:QUrl = modelPath
        self.__m_vtkFboRenderer:SquircleInFboRenderer = vtkFboRenderer

    def run(self):
        qDebug('CommandModelAdd::run()')

        self.__m_model = self.__m_processingEngine.addModel(self.__m_modelPath)
        self.__m_processingEngine.placeModel(self.__m_model)

        self.__m_ready = True
        self.signal_conn.ready.emit()


    def isReady(self) -> bool:
        return self.__m_ready

    def execute(self):
        qDebug('CommandModelAdd::execute()')

        self.__m_vtkFboRenderer.squircle.addModelActor(self.__m_model)
        self.signal_conn.done.emit()
