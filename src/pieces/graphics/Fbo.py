from PySide2.QtCore import QObject, QUrl, qDebug, qCritical, QEvent, QPoint, QPointF, Qt, Signal
from PySide2.QtGui import QColor, QMouseEvent, QWheelEvent
from PySide2.QtQuick import QQuickFramebufferObject

from src.pieces.commands import CommandModel
# from CommandModelAdd import CommandModelAdd
# from CommandModelTranslate import CommandModelTranslate, TranslateParams_t
# from ProcessingEngine import ProcessingEngine
from src.pieces.graphics import FboRenderer
from src.utils import cloneMouseEvent
import logging

class FboItem(QQuickFramebufferObject):
    # rendererInitialized = Signal()
    # isModelSelectedChanged = Signal(bool)
    # selectedModelPositionXChanged = Signal(float)
    # selectedModelPositionYChanged = Signal(float)

    # addModelFromFileDone = Signal()
    # addModelFromFileError = Signal(str)

    def __init__(self):
        super().__init__()
        self.__fboRenderer = None

        # self.__modelsRepresentationOption:int = 2
        # self.__modelsOpacity:float = 1.0
        # self.__gouraudInterpolation:bool = False
        # self.__modelColorR:int = 3
        # self.__modelColorG:int = 169
        # self.__modelColorB:int = 244

        # self.__lastMouseLeftButton:QMouseEvent = None
        # self.__lastMouseButton:QMouseEvent = None
        # self.__lastMouseMove:QMouseEvent = None

        # self.setMirrorVertically(True) # QtQuick and OpenGL have opposite Y-Axis directions
        # self.setAcceptedMouseButtons(Qt.AllButtons)

    def createRenderer(self) -> QQuickFramebufferObject.Renderer:
        self.__fboRenderer = FboRenderer()
        return self.__fboRenderer

    # def setVtkFboRenderer(self, renderer):
    #     logging.debug('FboItem::setVtkFboRenderer')

    #     self.__fboRenderer = renderer
    #     self.__fboRenderer.renderer.setVtkFboItem(self)

    #     self.__fboRenderer.renderer.isModelSelectedChanged.connect(self.isModelSelectedChanged)
    #     self.__fboRenderer.renderer.selectedModelPositionXChanged.connect(self.selectedModelPositionXChanged)
    #     self.__fboRenderer.renderer.selectedModelPositionYChanged.connect(self.selectedModelPositionYChanged)

    #     # self.__fboRenderer.renderer.setProcessingEngine(self.__processingEngine)
    #     self.rendererInitialized.emit()

    # #* Model releated functions

    # def isModelSelected(self) -> bool:
    #     return self.__fboRenderer.renderer.isModelSelected()

    # def getSelectedModelPositionX(self) -> float:
    #     return self.__fboRenderer.renderer.getSelectedModelPositionX()

    # def getSelectedModelPositionY(self) -> float:
    #     return self.__fboRenderer.renderer.getSelectedModelPositionY()

    # def selectModel(self, screenX:int, screenY:int):
    #     self.__lastMouseLeftButton = QMouseEvent(QEvent.Type.None_, QPointF(screenX, screenY), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
    #     self.__lastMouseLeftButton.ignore()
    #     self.update()

    # def resetModelSelection(self):
    #     self.__lastMouseLeftButton = QMouseEvent(QEvent.None_, QPointF(-1, -1), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
    #     self.__lastMouseLeftButton.ignore()
    #     self.update()

    # def addModelFromFile(self, modelPath):
    #     qDebug('FboItem::addModelFromFile')

    #     command = CommandModelAdd(self.__fboRenderer, self.__processingEngine, modelPath)

    #     command.signal_conn.ready.connect(self.update)
    #     command.signal_conn.done.connect(self.addModelFromFileDone)

    #     command.start()
    #     self.__addCommand(command)

    # def translateModel(self, translateData:TranslateParams_t, inTransition:bool):
    #     if translateData.model == None:
    #         #* If no model selected yet, try to select one
    #         translateData.model = self.__fboRenderer.renderer.getSelectedModel()

    #         if translateData.model == None:
    #             return

    #     self.__addCommand(CommandModelTranslate(self.__fboRenderer, translateData, inTransition))


    # def addCommand(self, command:CommandModel):
    #     with self.__fboRenderer.commandQueueLock:
    #         self.__fboRenderer.commandQueue.put(command)
    #     self.update()


    # #* Camera related functions

    # def wheelEvent(self, e:QWheelEvent):
    #     self.__lastMouseWheel = QWheelEvent(e)
    #     self.__lastMouseWheel.ignore()
    #     e.accept()
    #     self.update()

    # def mousePressEvent(self, e:QMouseEvent):
    #     self.__processMouseButtonEvent(e)

    # def mouseReleaseEvent(self, e:QMouseEvent):
    #     self.__processMouseButtonEvent(e)

    # def __processMouseButtonEvent(self, event: QMouseEvent):
    #     self.__lastMouseButton = cloneMouseEvent(event)
    #     self.__lastMouseButton.ignore()
    #     event.accept()
    #     self.update()

    # def mouseMoveEvent(self, e:QMouseEvent):
    #     self.__lastMouseMove = cloneMouseEvent(e)
    #     self.__lastMouseMove.ignore()
    #     e.accept()
    #     self.update()


    # def getLastMouseLeftButton(self, clone=True) -> QMouseEvent:
    #     if clone:
    #         return cloneMouseEvent(self.__lastMouseLeftButton)
    #     else:
    #         return self.__lastMouseLeftButton

    # def getLastMouseButton(self, clone=True) -> QMouseEvent:
    #     if clone:
    #         return cloneMouseEvent(self.__lastMouseButton)
    #     else:
    #         return self.__lastMouseButton

    # def getLastMoveEvent(self, clone=True) -> QMouseEvent:
    #     if clone:
    #         return cloneMouseEvent(self.__lastMouseMove)
    #     else:
    #         return self.__lastMouseMove

    # # def getLastWheelEvent(self) -> QWheelEvent:
    # #     return self.__lastMouseWheel


    # def resetCamera(self):
    #     self.__fboRenderer.renderer.resetCamera()
    #     self.update()

    # def getModelsRepresentation(self) -> int:
    #     return self.__modelsRepresentationOption

    # def getModelsOpacity(self) -> float:
    #     return self.__modelsOpacity

    # def getGourauInterpolation(self) -> bool:
    #     return self.__gouraudInterpolation

    # def getModelColorR(self) -> int:
    #     return self.__modelColorR

    # def getModelColorG(self) -> int:
    #     return self.__modelColorG

    # def getModelColorB(self) -> int:
    #     return self.__modelColorB

    # def setModelsRepresentation(self, representationOption:int):
    #     if self.__modelsRepresentationOption != representationOption:
    #         self.__modelsRepresentationOption = representationOption
    #         self.update()

    # def setModelsOpacity(self, opacity:float):
    #     if self.__modelsOpacity != opacity:
    #         self.__modelsOpacity = opacity
    #         self.update()

    # def setGouraudInterpolation(self, gouraudInterpolation:bool):
    #     if self.__gouraudInterpolation != gouraudInterpolation:
    #         self.__gouraudInterpolation = gouraudInterpolation
    #         self.update()

    # def setModelColorR(self, colorR:int):
    #     if self.__modelColorR != colorR:
    #         self.__modelColorR = colorR
    #         self.update()

    # def setModelColorG(self, colorG:int):
    #     if self.__modelColorG != colorG:
    #         self.__modelColorG = colorG
    #         self.update()

    # def setModelColorB(self, colorB:int):
    #     if self.__modelColorB != colorB:
    #         self.__modelColorB = colorB
    #         self.update()

    # def getCommandsQueueFront(self) -> CommandModel:
    #     return self.__commandsQueue.queue[0]

    # def commandsQueuePop(self):
    #     self.__commandsQueue.get()

    # def isCommandsQueueEmpty(self) -> bool:
    #     return self.__commandsQueue.empty()

    # def lockCommandsQueueMutex(self):
    #     self.__commandsQueueLock.acquire()

    # def unlockCommandsQueueMutex(self):
    #     self.__commandsQueueLock.release()
