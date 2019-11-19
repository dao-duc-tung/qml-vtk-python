from PyQt5.QtCore import QObject, QApp, QUrl, qDebug, qCritical, QEvent, QPointF, Q_FLAGS, Qt
from PyQt5.QtGui import QColor, QMouseEvent, QWheelEvent
from PyQt5.QtQuick import QQuickFramebufferObject

from .CommandModelAdd import CommandModelAdd
from .CommandModelTranslate import CommandModelTranslate, TranslateParams_t
from .ProcessingEngine import ProcessingEngine
from .QVTKFramebufferObjectRenderer import QVTKFramebufferObjectRenderer
import queue
import threading

class QVTKFramebufferObjectItem(QQuickFramebufferObject):
    def __init__(self):
        self.__m_vtkFboRenderer:QVTKFramebufferObjectRenderer = None
        self.__m_processingEngine:ProcessingEngine = ProcessingEngine()

        self.__m_commandsQueue:queue.Queue = queue.Queue() # CommandModel
        self.__m_commandsQueueMutex = threading.Lock()

        self.__m_modelsRepresentationOption:int = 2
        self.__m_modelsOpacity:float = 1.0
        self.__m_gouraudInterpolation:bool = False
        self.__m_modelColorR:int = 3
        self.__m_modelColorG:int = 169
        self.__m_modelColorB:int = 244

        self.__m_lastMouseLeftButton:QMouseEvent = QMouseEvent(QEvent.None, QPointF(0,0), Qt.NoButton, Qt.NoButton, Qt.NoModifier)
        self.__m_lastMouseButton = QMouseEvent(QEvent.None, QPointF(0,0), Qt.NoButton, Qt.NoButton, Qt.NoModifier)
        self.__m_lastMouseMove = QMouseEvent(QEvent.None, QPointF(0,0), Qt.NoButton, Qt.NoButton, Qt.NoModifier)
        self.__m_lastMouseWheel = QWheelEvent(QPointF(0,0), 0, Qt.NoButton, Qt.NoModifier, Qt.Vertical)

        self.setMirrorVertically(True) # QtQuick and OpenGL have opposite Y-Axis directions
        setAcceptedMouseButtons(Qt.RightButton)

    def createRenderer(self) -> QQuickFramebufferObject::Renderer:
        return QVTKFramebufferObjectRenderer()

    def setVtkFboRenderer(self, renderer:QVTKFramebufferObjectRenderer):
        qDebug('QVTKFramebufferObjectItem::setVtkFboRenderer')

        self.__m_vtkFboRenderer = renderer

        # TODO
        # connect(self.__m_vtkFboRenderer, &QVTKFramebufferObjectRenderer::isModelSelectedChanged, this, &QVTKFramebufferObjectItem::isModelSelectedChanged)
        # connect(self.__m_vtkFboRenderer, &QVTKFramebufferObjectRenderer::selectedModelPositionXChanged, this, &QVTKFramebufferObjectItem::selectedModelPositionXChanged)
        # connect(self.__m_vtkFboRenderer, &QVTKFramebufferObjectRenderer::selectedModelPositionYChanged, this, &QVTKFramebufferObjectItem::selectedModelPositionYChanged)

        self.__m_vtkFboRenderer.setProcessingEngine(self.__m_processingEngine)

    def isInitialized() -> bool:
        return (self.__m_vtkFboRenderer != None)

    def setProcessingEngine(self, processingEngine:ProcessingEngine):
        self.__m_processingEngine = processingEngine

    #* Model releated functions

    def isModelSelected() -> bool:
        return self.__m_vtkFboRenderer.isModelSelected()

    def getSelectedModelPositionX() -> float:
        return self.__m_vtkFboRenderer.getSelectedModelPositionX()

    def getSelectedModelPositionY() -> float:
        return self.__m_vtkFboRenderer.getSelectedModelPositionY()

    def selectModel(self, screenX:int, screenY:int):
        self.__m_lastMouseLeftButton = QMouseEvent(QEvent.None, QPointF(screenX, screenY), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
        self.__m_lastMouseLeftButton.ignore()
        update()

    def resetModelSelection(self):
        self.__m_lastMouseLeftButton = QMouseEvent(QEvent.None, QPointF(-1, -1), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
        self.__m_lastMouseLeftButton.ignore()
        update()

    def addModelFromFile(self, modelPath:QUrl):
        qDebug('QVTKFramebufferObjectItem::addModelFromFile')

        command = CommandModelAdd(self.__m_vtkFboRenderer, self.__m_processingEngine, modelPath)

        # TODO
        # connect(command, &CommandModelAdd::ready, this, &QVTKFramebufferObjectItem::update)
        # connect(command, &CommandModelAdd::done, this, &QVTKFramebufferObjectItem::addModelFromFileDone)

        command.start()
        self.__addCommand(command)

    def translateModel(self, translateData:TranslateParams_t, inTransition:bool):
        if translateData.model == None:
            # If no model selected yet, try to select one
            translateData.model = self.__m_vtkFboRenderer.getSelectedModel()

            if translateData.model == None:
                return

        self.__addCommand(CommandModelTranslate(self.__m_vtkFboRenderer, translateData, inTransition))


    def __addCommand(self, command:CommandModel):
        self.__m_commandsQueueMutex.acquire()
        self.__m_commandsQueue.push(command)
        self.__m_commandsQueueMutex.release()
        update()


    #* Camera related functions

    def wheelEvent(self, e:QWheelEvent):
        self.__m_lastMouseWheel = QWheelEvent(e)
        self.__m_lastMouseWheel.ignore()
        e.accept()
        update()

    def mousePressEvent(self, e:QMouseEvent):
        if e.buttons() & Qt.RightButton:
            self.__m_lastMouseButton = QMouseEvent(e)
            self.__m_lastMouseButton.ignore()
            e.accept()
            update()

    def mouseReleaseEvent(self, e:QMouseEvent):
        self.__m_lastMouseButton = QMouseEvent(e)
        self.__m_lastMouseButton.ignore()
        e.accept()
        update()

    def mouseMoveEvent(self, e:QMouseEvent):
        if e.buttons() & Qt.RightButton:
            self.__m_lastMouseMove = e
            self.__m_lastMouseMove.ignore()
            e.accept()
            update()


    def getLastMouseLeftButton() -> QMouseEvent:
        return self.__m_lastMouseLeftButton.get()

    def getLastMouseButton() -> QMouseEvent:
        return self.__m_lastMouseButton.get()

    def getLastMoveEvent() -> QMouseEvent:
        return self.__m_lastMouseMove.get()

    def getLastWheelEvent() -> QWheelEvent:
        return self.__m_lastMouseWheel.get()


    def resetCamera(self):
        self.__m_vtkFboRenderer.resetCamera()
        update()

    def getModelsRepresentation() -> int:
        return self.__m_modelsRepresentationOption

    def getModelsOpacity() -> float:
        return self.__m_modelsOpacity

    def getGourauInterpolation() -> bool:
        return self.__m_gouraudInterpolation

    def getModelColorR() -> int:
        return self.__m_modelColorR

    def getModelColorG() -> int:
        return self.__m_modelColorG

    def getModelColorB() -> int:
        return self.__m_modelColorB

    def setModelsRepresentation(self, representationOption:int):
        if self.__m_modelsRepresentationOption != representationOption:
            self.__m_modelsRepresentationOption = representationOption
            update()

    def setModelsOpacity(self, opacity:float):
        if self.__m_modelsOpacity != opacity:
            self.__m_modelsOpacity = opacity
            update()

    def setGouraudInterpolation(self, gouraudInterpolation:bool):
        if self.__m_gouraudInterpolation != gouraudInterpolation:
            self.__m_gouraudInterpolation = gouraudInterpolation
            update()

    def setModelColorR(self, colorR:int):
        if self.__m_modelColorR != colorR:
            self.__m_modelColorR = colorR
            update()

    def setModelColorG(self, colorG:int):
        if self.__m_modelColorG != colorG:
            self.__m_modelColorG = colorG
            update()

    def setModelColorB(self, colorB:int):
        if self.__m_modelColorB != colorB:
            self.__m_modelColorB = colorB
            update()

    def getCommandsQueueFront(self) -> CommandModel:
        return self.__m_commandsQueue.queue[0]

    def commandsQueuePop(self):
        self.__m_commandsQueue.get()

    def isCommandsQueueEmpty() -> bool:
        return self.__m_commandsQueue.empty()

    def lockCommandsQueueMutex(self):
        self.__m_commandsQueueMutex.acquire()

    def unlockCommandsQueueMutex(self):
        self.__m_commandsQueueMutex.release()
