from PySide2.QtCore import QObject, QUrl, qDebug, qCritical, QEvent, QPoint, QPointF, Qt, Signal
from PySide2.QtGui import QColor, QMouseEvent, QWheelEvent
from PySide2.QtQuick import QQuickFramebufferObject

from CommandModelAdd import CommandModel
from CommandModelAdd import CommandModelAdd
from CommandModelTranslate import CommandModelTranslate, TranslateParams_t
from ProcessingEngine import ProcessingEngine
from QVTKFramebufferObjectRenderer import FboRenderer
import queue
import threading
import logging

class FboItem(QQuickFramebufferObject):
    rendererInitialized = Signal()
    isModelSelectedChanged = Signal(bool)
    selectedModelPositionXChanged = Signal(float)
    selectedModelPositionYChanged = Signal(float)

    addModelFromFileDone = Signal()
    addModelFromFileError = Signal(str)

    def __init__(self):
        logging.debug('FboItem::__init__')
        super().__init__()
        self.__vtkFboRenderer = None
        self.__processingEngine:ProcessingEngine = None

        self.__commandsQueue:queue.Queue = queue.Queue() # CommandModel
        self.__commandsQueueMutex = threading.Lock()

        self.__modelsRepresentationOption:int = 2
        self.__modelsOpacity:float = 1.0
        self.__gouraudInterpolation:bool = False
        self.__modelColorR:int = 3
        self.__modelColorG:int = 169
        self.__modelColorB:int = 244

        self.__lastMouseLeftButton:QMouseEvent = QMouseEvent(QEvent.Type.None_, QPointF(0,0), Qt.NoButton, Qt.NoButton, Qt.NoModifier)
        self.__lastMouseButton:QMouseEvent = QMouseEvent(QEvent.Type.None_, QPointF(0,0), Qt.NoButton, Qt.NoButton, Qt.NoModifier)
        self.__lastMouseMove:QMouseEvent = QMouseEvent(QEvent.Type.None_, QPointF(0,0), Qt.NoButton, Qt.NoButton, Qt.NoModifier)
        # self.__lastMouseWheel:QWheelEvent = QWheelEvent(QPointF(0,0), 0, Qt.NoButton, Qt.NoModifier, Qt.Vertical)
        # self.__lastMouseWheel:QWheelEvent = QWheelEvent(QPointF(0,0), QPointF(0,0), QPoint(0,0), QPoint(0,0), 0, Qt.Vertical, Qt.NoButton, Qt.NoModifier)

        self.setMirrorVertically(True) # QtQuick and OpenGL have opposite Y-Axis directions
        self.setAcceptedMouseButtons(Qt.RightButton)

    def createRenderer(self):
        logging.debug('FboItem::createRenderer')
        self.setVtkFboRenderer(FboRenderer())
        return self.__vtkFboRenderer

    def setVtkFboRenderer(self, renderer):
        logging.debug('FboItem::setVtkFboRenderer')

        self.__vtkFboRenderer = renderer
        self.__vtkFboRenderer.renderer.setVtkFboItem(self)

        self.__vtkFboRenderer.renderer.isModelSelectedChanged.connect(self.isModelSelectedChanged)
        self.__vtkFboRenderer.renderer.selectedModelPositionXChanged.connect(self.selectedModelPositionXChanged)
        self.__vtkFboRenderer.renderer.selectedModelPositionYChanged.connect(self.selectedModelPositionYChanged)

        self.__vtkFboRenderer.renderer.setProcessingEngine(self.__processingEngine)
        self.rendererInitialized.emit()

    def isInitialized(self) -> bool:
        return (self.__vtkFboRenderer != None)

    def setProcessingEngine(self, processingEngine:ProcessingEngine):
        self.__processingEngine = processingEngine

    # #* Model releated functions

    def isModelSelected(self) -> bool:
        return self.__vtkFboRenderer.renderer.isModelSelected()

    def getSelectedModelPositionX(self) -> float:
        return self.__vtkFboRenderer.renderer.getSelectedModelPositionX()

    def getSelectedModelPositionY(self) -> float:
        return self.__vtkFboRenderer.renderer.getSelectedModelPositionY()

    def selectModel(self, screenX:int, screenY:int):
        self.__lastMouseLeftButton = QMouseEvent(QEvent.Type.None_, QPointF(screenX, screenY), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
        self.__lastMouseLeftButton.ignore()
        self.update()

    def resetModelSelection(self):
        self.__lastMouseLeftButton = QMouseEvent(QEvent.None_, QPointF(-1, -1), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
        self.__lastMouseLeftButton.ignore()
        self.update()

    def addModelFromFile(self, modelPath):
        qDebug('FboItem::addModelFromFile')

        command = CommandModelAdd(self.__vtkFboRenderer, self.__processingEngine, modelPath)

        command.signal_conn.ready.connect(self.update)
        command.signal_conn.done.connect(self.addModelFromFileDone)

        command.start()
        self.__addCommand(command)

    def translateModel(self, translateData:TranslateParams_t, inTransition:bool):
        if translateData.model == None:
            #* If no model selected yet, try to select one
            translateData.model = self.__vtkFboRenderer.renderer.getSelectedModel()

            if translateData.model == None:
                return

        self.__addCommand(CommandModelTranslate(self.__vtkFboRenderer, translateData, inTransition))


    def __addCommand(self, command:CommandModel):
        self.__commandsQueueMutex.acquire()
        self.__commandsQueue.put(command)
        self.__commandsQueueMutex.release()
        self.update()


    # #* Camera related functions

    # def wheelEvent(self, e:QWheelEvent):
    #     self.__lastMouseWheel = QWheelEvent(e)
    #     self.__lastMouseWheel.ignore()
    #     e.accept()
    #     self.update()

    def mousePressEvent(self, e:QMouseEvent):
        if e.buttons() & Qt.RightButton:
            self.__lastMouseButton = self.__cloneMouseEvent(e)
            self.__lastMouseButton.ignore()
            e.accept()
            self.update()

    def mouseReleaseEvent(self, e:QMouseEvent):
        self.__lastMouseButton = self.__cloneMouseEvent(e)
        self.__lastMouseButton.ignore()
        e.accept()
        self.update()

    def mouseMoveEvent(self, e:QMouseEvent):
        if e.buttons() & Qt.RightButton:
            self.__lastMouseMove = self.__cloneMouseEvent(e)
            self.__lastMouseMove.ignore()
            e.accept()
            self.update()


    def getLastMouseLeftButton(self, clone=True) -> QMouseEvent:
        if clone:
            return self.__cloneMouseEvent(self.__lastMouseLeftButton)
        else:
            return self.__lastMouseLeftButton

    def getLastMouseButton(self, clone=True) -> QMouseEvent:
        if clone:
            return self.__cloneMouseEvent(self.__lastMouseButton)
        else:
            return self.__lastMouseButton

    def getLastMoveEvent(self, clone=True) -> QMouseEvent:
        if clone:
            return self.__cloneMouseEvent(self.__lastMouseMove)
        else:
            return self.__lastMouseMove

    # def getLastWheelEvent(self) -> QWheelEvent:
    #     return self.__lastMouseWheel


    def resetCamera(self):
        self.__vtkFboRenderer.renderer.resetCamera()
        self.update()

    def getModelsRepresentation(self) -> int:
        return self.__modelsRepresentationOption

    def getModelsOpacity(self) -> float:
        return self.__modelsOpacity

    def getGourauInterpolation(self) -> bool:
        return self.__gouraudInterpolation

    def getModelColorR(self) -> int:
        return self.__modelColorR

    def getModelColorG(self) -> int:
        return self.__modelColorG

    def getModelColorB(self) -> int:
        return self.__modelColorB

    def setModelsRepresentation(self, representationOption:int):
        if self.__modelsRepresentationOption != representationOption:
            self.__modelsRepresentationOption = representationOption
            self.update()

    def setModelsOpacity(self, opacity:float):
        if self.__modelsOpacity != opacity:
            self.__modelsOpacity = opacity
            self.update()

    def setGouraudInterpolation(self, gouraudInterpolation:bool):
        if self.__gouraudInterpolation != gouraudInterpolation:
            self.__gouraudInterpolation = gouraudInterpolation
            self.update()

    def setModelColorR(self, colorR:int):
        if self.__modelColorR != colorR:
            self.__modelColorR = colorR
            self.update()

    def setModelColorG(self, colorG:int):
        if self.__modelColorG != colorG:
            self.__modelColorG = colorG
            self.update()

    def setModelColorB(self, colorB:int):
        if self.__modelColorB != colorB:
            self.__modelColorB = colorB
            self.update()

    def getCommandsQueueFront(self) -> CommandModel:
        return self.__commandsQueue.queue[0]

    def commandsQueuePop(self):
        self.__commandsQueue.get()

    def isCommandsQueueEmpty(self) -> bool:
        return self.__commandsQueue.empty()

    def lockCommandsQueueMutex(self):
        self.__commandsQueueMutex.acquire()

    def unlockCommandsQueueMutex(self):
        self.__commandsQueueMutex.release()

    def __cloneMouseEvent(self, e:QMouseEvent):
        event_type = e.type()
        local_pos = e.localPos()
        button = e.button()
        buttons = e.buttons()
        modifiers = e.modifiers()
        clone = QMouseEvent(event_type, local_pos, button, buttons, modifiers)
        clone.ignore()
        return clone
