from PyQt5.QtCore import QObject, QApp, QUrl, qDebug, qCritical, QFileInfo, QThread, pyqtSignal

from .ProcessingEngine import ProcessingEngine
from .CommandModel import CommandModel
from .Model import Model
from .QVTKFramebufferObjectRenderer import QVTKFramebufferObjectRenderer

class CommandModelAdd(QThread, CommandModel):
    ready = pyqtSignal()
	done = pyqtSignal()

    def __init__(self, vtkFboRenderer:QVTKFramebufferObjectRenderer, processingEngine:ProcessingEngine, modelPath:QUrl):
        self.__m_model:Model = None
        self.__m_positionX:float = 0.0
        self.__m_positionY:float = 0.0
        self.__m_ready:bool = False

        self.__m_processingEngine:ProcessingEngine = processingEngine
        self.__m_modelPath:QUrl = modelPath
        self._m_vtkFboRenderer:QVTKFramebufferObjectRenderer = vtkFboRenderer

    def run(self):
        qDebug('CommandModelAdd::run()')

        self.__m_model = self.__m_processingEngine.addModel(self.__m_modelPath)
        self.__m_processingEngine.placeModel(self.__m_model)

        self.__m_ready = True
        self.ready.emit()


    def isReady() -> bool:
        return self.__m_ready

    def execute(self):
        qDebug('CommandModelAdd::execute()')

        self._m_vtkFboRenderer.addModelActor(self.__m_model)

        self.done.emit()
