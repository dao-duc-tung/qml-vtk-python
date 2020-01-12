from PySide2.QtCore import QObject, QUrl, qDebug, qCritical, QEvent, QPoint, QPointF, Qt, Signal
from PySide2.QtGui import QColor, QMouseEvent, QWheelEvent, QSurfaceFormat
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
        self.__m_vtkFboRenderer = None
        self.__m_processingEngine:ProcessingEngine = None

        self.__m_commandsQueue:queue.Queue = queue.Queue() # CommandModel
        self.__m_commandsQueueMutex = threading.Lock()

        self.__m_modelsRepresentationOption:int = 2
        self.__m_modelsOpacity:float = 1.0
        self.__m_gouraudInterpolation:bool = False
        self.__m_modelColorR:int = 3
        self.__m_modelColorG:int = 169
        self.__m_modelColorB:int = 244

        self.__m_lastMouseLeftButton:QMouseEvent = QMouseEvent(QEvent.Type.None_, QPointF(0,0), Qt.NoButton, Qt.NoButton, Qt.NoModifier)
        self.__m_lastMouseButton:QMouseEvent = QMouseEvent(QEvent.Type.None_, QPointF(0,0), Qt.NoButton, Qt.NoButton, Qt.NoModifier)
        self.__m_lastMouseMove:QMouseEvent = QMouseEvent(QEvent.Type.None_, QPointF(0,0), Qt.NoButton, Qt.NoButton, Qt.NoModifier)
        # self.__m_lastMouseWheel:QWheelEvent = QWheelEvent(QPointF(0,0), 0, Qt.NoButton, Qt.NoModifier, Qt.Vertical)
        # self.__m_lastMouseWheel:QWheelEvent = QWheelEvent(QPointF(0,0), QPointF(0,0), QPoint(0,0), QPoint(0,0), 0, Qt.Vertical, Qt.NoButton, Qt.NoModifier)

        self.setMirrorVertically(True) # QtQuick and OpenGL have opposite Y-Axis directions
        self.setAcceptedMouseButtons(Qt.RightButton)

    def createRenderer(self):
        logging.debug('FboItem::createRenderer')
        self.setVtkFboRenderer(FboRenderer())
        return self.__m_vtkFboRenderer

    def setVtkFboRenderer(self, renderer):
        logging.debug('FboItem::setVtkFboRenderer')

        self.__m_vtkFboRenderer = renderer
        self.__m_vtkFboRenderer.renderer.setVtkFboItem(self)

        self.__m_vtkFboRenderer.renderer.isModelSelectedChanged.connect(self.isModelSelectedChanged)
        self.__m_vtkFboRenderer.renderer.selectedModelPositionXChanged.connect(self.selectedModelPositionXChanged)
        self.__m_vtkFboRenderer.renderer.selectedModelPositionYChanged.connect(self.selectedModelPositionYChanged)

        self.__m_vtkFboRenderer.renderer.setProcessingEngine(self.__m_processingEngine)
        self.rendererInitialized.emit()

    def isInitialized(self) -> bool:
        return (self.__m_vtkFboRenderer != None)

    def setProcessingEngine(self, processingEngine:ProcessingEngine):
        self.__m_processingEngine = processingEngine

    # #* Model releated functions

    def isModelSelected(self) -> bool:
        return self.__m_vtkFboRenderer.renderer.isModelSelected()

    def getSelectedModelPositionX(self) -> float:
        return self.__m_vtkFboRenderer.renderer.getSelectedModelPositionX()

    def getSelectedModelPositionY(self) -> float:
        return self.__m_vtkFboRenderer.renderer.getSelectedModelPositionY()

    def selectModel(self, screenX:int, screenY:int):
        self.__m_lastMouseLeftButton = QMouseEvent(QEvent.Type.None_, QPointF(screenX, screenY), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
        self.__m_lastMouseLeftButton.ignore()
        self.update()

    def resetModelSelection(self):
        self.__m_lastMouseLeftButton = QMouseEvent(QEvent.None_, QPointF(-1, -1), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
        self.__m_lastMouseLeftButton.ignore()
        self.update()

    def addModelFromFile(self, modelPath):
        qDebug('FboItem::addModelFromFile')

        command = CommandModelAdd(self.__m_vtkFboRenderer, self.__m_processingEngine, modelPath)

        command.signal_conn.ready.connect(self.update)
        command.signal_conn.done.connect(self.addModelFromFileDone)

        command.start()
        self.__addCommand(command)

    def translateModel(self, translateData:TranslateParams_t, inTransition:bool):
        if translateData.model == None:
            #* If no model selected yet, try to select one
            translateData.model = self.__m_vtkFboRenderer.renderer.getSelectedModel()

            if translateData.model == None:
                return

        self.__addCommand(CommandModelTranslate(self.__m_vtkFboRenderer, translateData, inTransition))


    def __addCommand(self, command:CommandModel):
        self.__m_commandsQueueMutex.acquire()
        self.__m_commandsQueue.put(command)
        self.__m_commandsQueueMutex.release()
        self.update()


    # #* Camera related functions

    # def wheelEvent(self, e:QWheelEvent):
    #     self.__m_lastMouseWheel = QWheelEvent(e)
    #     self.__m_lastMouseWheel.ignore()
    #     e.accept()
    #     self.update()

    def mousePressEvent(self, e:QMouseEvent):
        if e.buttons() & Qt.RightButton:
            self.__m_lastMouseButton = self.__cloneMouseEvent(e)
            self.__m_lastMouseButton.ignore()
            e.accept()
            self.update()

    def mouseReleaseEvent(self, e:QMouseEvent):
        self.__m_lastMouseButton = self.__cloneMouseEvent(e)
        self.__m_lastMouseButton.ignore()
        e.accept()
        self.update()

    def mouseMoveEvent(self, e:QMouseEvent):
        if e.buttons() & Qt.RightButton:
            self.__m_lastMouseMove = self.__cloneMouseEvent(e)
            self.__m_lastMouseMove.ignore()
            e.accept()
            self.update()


    def getLastMouseLeftButton(self, clone=True) -> QMouseEvent:
        if clone:
            return self.__cloneMouseEvent(self.__m_lastMouseLeftButton)
        else:
            return self.__m_lastMouseLeftButton

    def getLastMouseButton(self, clone=True) -> QMouseEvent:
        if clone:
            return self.__cloneMouseEvent(self.__m_lastMouseButton)
        else:
            return self.__m_lastMouseButton

    def getLastMoveEvent(self, clone=True) -> QMouseEvent:
        if clone:
            return self.__cloneMouseEvent(self.__m_lastMouseMove)
        else:
            return self.__m_lastMouseMove

    # def getLastWheelEvent(self) -> QWheelEvent:
    #     return self.__m_lastMouseWheel


    def resetCamera(self):
        self.__m_vtkFboRenderer.renderer.resetCamera()
        self.update()

    def getModelsRepresentation(self) -> int:
        return self.__m_modelsRepresentationOption

    def getModelsOpacity(self) -> float:
        return self.__m_modelsOpacity

    def getGourauInterpolation(self) -> bool:
        return self.__m_gouraudInterpolation

    def getModelColorR(self) -> int:
        return self.__m_modelColorR

    def getModelColorG(self) -> int:
        return self.__m_modelColorG

    def getModelColorB(self) -> int:
        return self.__m_modelColorB

    def setModelsRepresentation(self, representationOption:int):
        if self.__m_modelsRepresentationOption != representationOption:
            self.__m_modelsRepresentationOption = representationOption
            self.update()

    def setModelsOpacity(self, opacity:float):
        if self.__m_modelsOpacity != opacity:
            self.__m_modelsOpacity = opacity
            self.update()

    def setGouraudInterpolation(self, gouraudInterpolation:bool):
        if self.__m_gouraudInterpolation != gouraudInterpolation:
            self.__m_gouraudInterpolation = gouraudInterpolation
            self.update()

    def setModelColorR(self, colorR:int):
        if self.__m_modelColorR != colorR:
            self.__m_modelColorR = colorR
            self.update()

    def setModelColorG(self, colorG:int):
        if self.__m_modelColorG != colorG:
            self.__m_modelColorG = colorG
            self.update()

    def setModelColorB(self, colorB:int):
        if self.__m_modelColorB != colorB:
            self.__m_modelColorB = colorB
            self.update()

    def getCommandsQueueFront(self) -> CommandModel:
        return self.__m_commandsQueue.queue[0]

    def commandsQueuePop(self):
        self.__m_commandsQueue.get()

    def isCommandsQueueEmpty(self) -> bool:
        return self.__m_commandsQueue.empty()

    def lockCommandsQueueMutex(self):
        self.__m_commandsQueueMutex.acquire()

    def unlockCommandsQueueMutex(self):
        self.__m_commandsQueueMutex.release()

    def __cloneMouseEvent(self, e:QMouseEvent):
        event_type = e.type()
        local_pos = e.localPos()
        button = e.button()
        buttons = e.buttons()
        modifiers = e.modifiers()
        clone = QMouseEvent(event_type, local_pos, button, buttons, modifiers)
        clone.ignore()
        return clone

    def defaultSurfaceFormat(stereo_capable):
        """ Ported from: https://github.com/Kitware/VTK/blob/master/GUISupport/Qt/QVTKRenderWindowAdapter.cxx
        """
        fmt = QSurfaceFormat()
        fmt.setRenderableType(QSurfaceFormat.OpenGL)
        fmt.setVersion(3, 2)
        fmt.setProfile(QSurfaceFormat.CoreProfile)
        fmt.setSwapBehavior(QSurfaceFormat.DoubleBuffer)
        fmt.setRedBufferSize(8)
        fmt.setGreenBufferSize(8)
        fmt.setBlueBufferSize(8)
        fmt.setDepthBufferSize(8)
        fmt.setAlphaBufferSize(8)
        fmt.setStencilBufferSize(0)
        fmt.setStereo(stereo_capable)
        fmt.setSamples(0)

        return fmt
