from PySide2.QtCore import QObject, QUrl, qDebug, qCritical, QFileInfo, QEvent, Qt, QSize, Signal
from PySide2.QtGui import QSurfaceFormat, QColor, QMouseEvent, QWheelEvent, QOpenGLFramebufferObject, QOpenGLFramebufferObjectFormat, QOpenGLFunctions
from PySide2.QtQuick import QQuickFramebufferObject

# from Model import Model, setSelectedModelColor
# from ProcessingEngine import ProcessingEngine
from src.utils import cloneMouseEvent

import numpy as np
import vtk
import logging
import threading
import queue


class FboRenderer(QQuickFramebufferObject.Renderer, QObject):
    # isModelSelectedChanged = Signal(bool)
    # selectedModelPositionXChanged = Signal(float)
    # selectedModelPositionYChanged = Signal(float)

    def __init__(self):
        super().__init__()
        self.__gl = QOpenGLFunctions()

        # self.__commandQueue = queue.Queue()
        # self.__lock = threading.Lock()

        # self.__processingEngine:ProcessingEngine = None

        # self.__selectedModel:Model = None
        # self.__selectedActor:vtk.vtkActor = None
        # self.__isModelSelected:bool = False

        # self.__selectedModelPositionX:float = 0.0
        # self.__selectedModelPositionY:float = 0.0

        # self.__mouseLeftButton:QMouseEvent = None
        # self.__mouseEvent:QMouseEvent = None
        # self.__moveEvent:QMouseEvent = None
        # # self.__wheelEvent:QWheelEvent = None

        # self.__platformModel:vtk.vtkCubeSource = None
        # self.__platformGrid:vtk.vtkPolyData = None
        # self.__platformModelActor:vtk.vtkActor = None
        # self.__platformGridActor:vtk.vtkActor = None

        # self.__platformWidth:float = 200.0
        # self.__platformDepth:float = 200.0
        # # self.__platformHeight:float = 200.0
        # self.__platformThickness:float = 2.0
        # self.__gridBottomHeight:float = 0.15
        # self.__gridSize:np.uint16 = 10

        # self.__camPositionX:float = 0.0
        # self.__camPositionY:float = 0.0
        # self.__camPositionZ:float = 0.0

        # self.__clickPositionZ:float = 0.0

        # self.__firstRender:bool = True

        # self.__modelsRepresentationOption:int = 0
        # self.__modelsOpacity:float = 1.0
        # self.__modelsGouraudInterpolation:bool = False

        self.__rw = vtk.vtkExternalOpenGLRenderWindow()
        self.__rwi = vtk.vtkGenericRenderWindowInteractor()
        self.__rwi.SetRenderWindow(self.__rw)
        self.__rw.OpenGLInitContext()
        self.__isOpenGLStateInitialized = False

        self.__openGLFbo = None
        self.__fboItem = None

        # self.__lastMouseButtonEvent:QMouseEvent = None
        # self.__lastMouseMoveEvent:QMouseEvent = None

        # style = vtk.vtkInteractorStyleTrackballCamera()
        # style.SetDefaultRenderer(self.__renderer)
        # style.SetMotionFactor(10.0)
        # self.__rwi.SetInteractorStyle(style)

        # self.__picker:vtk.vtkCellPicker = vtk.vtkCellPicker()
        # self.__picker.SetTolerance(0.0)

    # def setVtkFboItem(self, vtkFboItem):
    #     qDebug('RendererHelper::setVtkFboItem()')
    #     self.__fboItem = vtkFboItem

    # def setProcessingEngine(self, processingEngine:ProcessingEngine):
    #     qDebug('RendererHelper::setProcessingEngine()')
    #     self.__processingEngine = processingEngine

    def createFramebufferObject(self, size:QSize) -> QOpenGLFramebufferObject:
        gl_format = QOpenGLFramebufferObjectFormat()
        gl_format.setAttachment(QOpenGLFramebufferObject.CombinedDepthStencil)
        self.__openGLFbo = QOpenGLFramebufferObject(size, gl_format)
        return self.__openGLFbo

    def synchronize(self, item:QQuickFramebufferObject):
        if not self.__fboItem:
            self.__fboItem = item

        # (w, h) = self._renderWindow.GetSize()
        # if int(self.__fboItem.width()) != w or int(self.__fboItem.height()) != h:
        #     self._renderWindow.SetSize(int(self.__fboItem.width()), int(self.__fboItem.height()))
        #     self.__isWindowSizeChanged = True

        # if self.__fboItem._lastMouseButtonEvent and not self.__fboItem._lastMouseButtonEvent.isAccepted():
        #     self.__lastMouseButtonEvent = cloneMouseEvent(self.__fboItem._lastMouseButtonEvent)
        #     self.__lastMouseButtonEvent.ignore()
        #     self.__fboItem._lastMouseButtonEvent.accept()
        # if self.__fboItem._lastMouseMoveEvent and not self.__fboItem._lastMouseMoveEvent.isAccepted():
        #     self.__lastMouseMoveEvent = cloneMouseEvent(self.__fboItem._lastMouseMoveEvent)
        #     self.__lastMouseMoveEvent.ignore()
        #     self.__fboItem._lastMouseMoveEvent.accept()

        #* Get extra data
        # self.__modelsRepresentationOption = self.__fboItem.getModelsRepresentation()
        # self.__modelsOpacity = self.__fboItem.getModelsOpacity()
        # self.__modelsGouraudInterpolation = self.__fboItem.getGourauInterpolation()
        # setSelectedModelColor(QColor(self.__fboItem.getModelColorR(), self.__fboItem.getModelColorG(), self.__fboItem.getModelColorB()))

    def render(self):
        if not self.__isOpenGLStateInitialized:
            self.__openGLInitState()
            self.__isOpenGLStateInitialized = True

        # if self.__lastMouseButtonEvent and not self.__lastMouseButtonEvent.isAccepted():
        #     self.__processMouseButtonEvent(self.__lastMouseButtonEvent)
        #     self.__lastMouseButtonEvent.accept()
        # if self.__lastMouseMoveEvent and not self.__lastMouseMoveEvent.isAccepted():
        #     self.__processMouseMoveEvent(self.__lastMouseMoveEvent)
        #     self.__lastMouseMoveEvent.accept()

        # with self.__lock:
        #     while not self.__commandQueue.empty():
        #         cmd = self.__commandQueue.get()
        #         cmd.SafeExecute()

        # #* Reset the view-up vector. self improves the interaction of the camera with the plate.
        # self.__renderer.GetActiveCamera().SetViewUp(0.0, 0.0, 1.0)

        # #* Extra actions
        # self.__processingEngine.setModelsRepresentation(self.__modelsRepresentationOption)
        # self.__processingEngine.setModelsOpacity(self.__modelsOpacity)
        # self.__processingEngine.setModelsGouraudInterpolation(self.__modelsGouraudInterpolation)
        # self.__processingEngine.updateModelsColor()

        # #* Render
        # self.__rw.Render()
        # self.__rw.PopState()

        self.__fboItem.window().resetOpenGLState()

    def __openGLInitState(self):
        self.__rw.OpenGLInitState()
        self.__rw.MakeCurrent()
        self.__gl.initializeOpenGLFunctions()
        self.__gl.glUseProgram(0)

    # def __processMouseButtonEvent(self, event: QMouseEvent):
    #     ctrl, shift = self.__getCtrlShift(event)
    #     if event.type() == QEvent.MouseButtonPress:
    #         repeat = 0
    #         self.__setEventInformation(event.x(), event.y(),
    #                                    ctrl, shift, chr(0), repeat, None)
    #         if event.button() == Qt.LeftButton:
    #             self.__rwi.LeftButtonPressEvent()
    #         elif event.button() == Qt.RightButton:
    #             self.__rwi.RightButtonPressEvent()
    #         elif event.button() == Qt.MidButton:
    #             self.__rwi.MiddleButtonPressEvent()
    #     elif event.type() == QEvent.MouseButtonDblClick:
    #         repeat = 1
    #         self.__setEventInformation(event.x(), event.y(),
    #                                    ctrl, shift, chr(0), repeat, None)
    #         if event.button() == Qt.LeftButton:
    #             self.__rwi.LeftButtonPressEvent()
    #         elif event.button() == Qt.RightButton:
    #             self.__rwi.RightButtonPressEvent()
    #         elif event.button() == Qt.MidButton:
    #             self.__rwi.MiddleButtonPressEvent()
    #     elif event.type() == QEvent.MouseButtonRelease:
    #         repeat = 0
    #         self.__setEventInformation(event.x(), event.y(),
    #                                    ctrl, shift, chr(0), repeat, None)
    #         if event.button() == Qt.LeftButton:
    #             self.__rwi.LeftButtonReleaseEvent()
    #         elif event.button() == Qt.RightButton:
    #             self.__rwi.RightButtonReleaseEvent()
    #         elif event.button() == Qt.MidButton:
    #             self.__rwi.MiddleButtonReleaseEvent()

    # def __processMouseMoveEvent(self, event: QMouseEvent):
    #     # This mouse move event only occurs when any mouse button is pressed
    #     ctrl, shift = self.__getCtrlShift(event)
    #     self.__saveX = event.x()
    #     self.__saveY = event.y()
    #     self.__setEventInformation(event.x(), event.y(),
    #                                ctrl, shift, chr(0), 0, None)
    #     self.__rwi.MouseMoveEvent()

    # def __setEventInformation(self, x, y, ctrl, shift, key, repeat=0, keysum=None):
    #     scale = self.__getPixelRatio()
    #     if self.__fboItem.mirrorVertically():
    #         (w, h) = self._renderWindow.GetSize()
    #         y = h - y

    #     self.__rwi.SetEventInformation(
    #         int(round(x * scale)),
    #         int(round(y * scale)),
    #         ctrl, shift, key, repeat, keysum
    #     )

    # def initScene(self):
    #     qDebug('RendererHelper::initScene()')

    #     self.__rw.SetOffScreenRendering(True)

    #     #* Top background color
    #     r2 = 245.0 / 255.0
    #     g2 = 245.0 / 255.0
    #     b2 = 245.0 / 255.0

    #     #* Bottom background color
    #     r1 = 170.0 / 255.0
    #     g1 = 170.0 / 255.0
    #     b1 = 170.0 / 255.0

    #     self.__renderer.SetBackground(r2, g2, b2)
    #     self.__renderer.SetBackground2(r1, g1, b1)
    #     self.__renderer.GradientBackgroundOn()

    #     # #* Axes
    #     axes = vtk.vtkAxesActor()
    #     axes_length = 20.0
    #     axes_label_font_size = np.int16(20)
    #     axes.SetTotalLength(axes_length, axes_length, axes_length)
    #     axes.GetXAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
    #     axes.GetYAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
    #     axes.GetZAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
    #     axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(axes_label_font_size)
    #     axes.GetYAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(axes_label_font_size)
    #     axes.GetZAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(axes_label_font_size)
    #     self.__renderer.AddActor(axes)

    #     # #* Platform
    #     self.__generatePlatform()

    #     #* Initial camera position
    #     self.resetCamera()

    # def __generatePlatform(self):
    #     qDebug('RendererHelper::__generatePlatform()')

    #     #* Platform Model
    #     platformModelMapper = vtk.vtkPolyDataMapper()

    #     self.__platformModel = vtk.vtkCubeSource()
    #     platformModelMapper.SetInputConnection(self.__platformModel.GetOutputPort())

    #     self.__platformModelActor = vtk.vtkActor()
    #     self.__platformModelActor.SetMapper(platformModelMapper)
    #     self.__platformModelActor.GetProperty().SetColor(1, 1, 1)
    #     self.__platformModelActor.GetProperty().LightingOn()
    #     self.__platformModelActor.GetProperty().SetOpacity(1)
    #     self.__platformModelActor.GetProperty().SetAmbient(0.45)
    #     self.__platformModelActor.GetProperty().SetDiffuse(0.4)

    #     self.__platformModelActor.PickableOff()
    #     self.__renderer.AddActor(self.__platformModelActor)

    #     #* Platform Grid
    #     self.__platformGrid = vtk.vtkPolyData()

    #     platformGridMapper = vtk.vtkPolyDataMapper()
    #     platformGridMapper.SetInputData(self.__platformGrid)

    #     self.__platformGridActor = vtk.vtkActor()
    #     self.__platformGridActor.SetMapper(platformGridMapper)
    #     self.__platformGridActor.GetProperty().LightingOff()
    #     self.__platformGridActor.GetProperty().SetColor(0.45, 0.45, 0.45)
    #     self.__platformGridActor.GetProperty().SetOpacity(1)
    #     self.__platformGridActor.PickableOff()
    #     self.__renderer.AddActor(self.__platformGridActor)

    #     self.__updatePlatform()

    # def __updatePlatform(self):
    #     qDebug('RendererHelper::__updatePlatform()')

    #     #* Platform Model

    #     if self.__platformModel:
    #         self.__platformModel.SetXLength(self.__platformWidth)
    #         self.__platformModel.SetYLength(self.__platformDepth)
    #         self.__platformModel.SetZLength(self.__platformThickness)
    #         self.__platformModel.SetCenter(0.0, 0.0, -self.__platformThickness / 2)

    #     #* Platform Grid
    #     gridPoints = vtk.vtkPoints()
    #     gridCells = vtk.vtkCellArray()

    #     i = -self.__platformWidth / 2
    #     while i <= self.__platformWidth / 2:
    #         self.__createLine(i, -self.__platformDepth / 2, self.__gridBottomHeight, i, self.__platformDepth / 2, self.__gridBottomHeight, gridPoints, gridCells)
    #         i += self.__gridSize

    #     i = -self.__platformDepth / 2
    #     while i <= self.__platformDepth / 2:
    #         self.__createLine(-self.__platformWidth / 2, i, self.__gridBottomHeight, self.__platformWidth / 2, i, self.__gridBottomHeight, gridPoints, gridCells)
    #         i += self.__gridSize

    #     self.__platformGrid.SetPoints(gridPoints)
    #     self.__platformGrid.SetLines(gridCells)

    # def __createLine(self, x1:float, y1:float, z1:float, x2:float, y2:float, z2:float, points:vtk.vtkPoints, cells:vtk.vtkCellArray):
    #     line = vtk.vtkPolyLine()
    #     line.GetPointIds().SetNumberOfIds(2)

    #     id_1 = points.InsertNextPoint(x1, y1, z1) # vtkIdType
    #     id_2 = points.InsertNextPoint(x2, y2, z2) # vtkIdType

    #     line.GetPointIds().SetId(0, id_1)
    #     line.GetPointIds().SetId(1, id_2)

    #     cells.InsertNextCell(line)

    # def addModelActor(self, model:Model):
    #     self.__renderer.AddActor(model.getModelActor())
    #     # qDebug(f'RendererHelper::addModelActor(): Model added {model}')

    # def __selectModel(self, x:np.int16, y:np.int16):
    #     qDebug('RendererHelper::__selectModel()')

    #     #*  the y-axis flip for the pickin:
    #     self.__picker.Pick(x, self.__renderer.GetSize()[1] - y, 0, self.__renderer)

    #     #* Get pick position
    #     # clickPosition = [0.0, 0.0, 0.0]
    #     # self.__picker.GetPickPosition(clickPosition)
    #     clickPosition = self.__picker.GetPickPosition()
    #     self.__clickPositionZ = clickPosition[2]

    #     if self.__selectedActor == self.__picker.GetActor():
    #         if self.__selectedModel:
    #             self.__selectedModel.setMouseDeltaXY(clickPosition[0] - self.__selectedModel.getPositionX(), clickPosition[1] - self.__selectedModel.getPositionY())
    #         return

    #     #* Disconnect signals
    #     if self.__selectedModel:
    #         self.__clearSelectedModel()

    #     #* Pick the new actor
    #     self.__selectedActor = self.__picker.GetActor()

    #     self.__selectedModel = self.__getSelectedModelNoLock()

    #     if self.__selectedActor:
    #         # qDebug(f'RendererHelper::__selectModel(): picked actor {self.__selectedActor}')

    #         self.__selectedModel.setSelected(True)

    #         #* Connect signals
    #         self.__selectedModel.positionXChanged.connect(self.setSelectedModelPositionX)
    #         self.__selectedModel.positionYChanged.connect(self.setSelectedModelPositionY)

    #         self.setSelectedModelPositionX(self.__selectedModel.getPositionX())
    #         self.setSelectedModelPositionY(self.__selectedModel.getPositionY())

    #         self.__setIsModelSelected(True)

    #         #* Set mouse click delta from center position
    #         self.__selectedModel.setMouseDeltaXY(clickPosition[0] - self.__selectedModel.getPositionX(), clickPosition[1] - self.__selectedModel.getPositionY())
    #     else:
    #         self.__setIsModelSelected(False)

    #     qDebug('RendererHelper::__selectModel() end')

    # def __clearSelectedModel(self):
    #     self.__selectedModel.setSelected(False)

    #     self.__selectedModel.positionXChanged.disconnect(self.setSelectedModelPositionX)
    #     self.__selectedModel.positionYChanged.disconnect(self.setSelectedModelPositionY)

    #     self.__selectedModel = None
    #     self.__selectedActor = None

    # def __setIsModelSelected(self, isModelSelected:bool):
    #     if self.__isModelSelected != isModelSelected:
    #         qDebug(f'RendererHelper::__setIsModelSelected(): {isModelSelected}')
    #         self.__isModelSelected = isModelSelected
    #         self.isModelSelectedChanged.emit(isModelSelected)

    # def isModelSelected(self) -> bool:
    #     return self.__isModelSelected

    # def getSelectedModel(self) -> Model:
    #     selectedModel = self.__getSelectedModelNoLock()
    #     return selectedModel

    # def __getSelectedModelNoLock(self) -> Model:
    #     return self.__processingEngine.getModelFromActor(self.__selectedActor)

    # def setSelectedModelPositionX(self, positionX:float):
    #     if self.__selectedModelPositionX != positionX:
    #         self.__selectedModelPositionX = positionX
    #         self.selectedModelPositionXChanged.emit(positionX)

    # def setSelectedModelPositionY(self, positionY:float):
    #     if self.__selectedModelPositionY != positionY:
    #         self.__selectedModelPositionY = positionY
    #         self.selectedModelPositionYChanged.emit(positionY)

    # def getSelectedModelPositionX(self) -> float:
    #     return self.__selectedModelPositionX

    # def getSelectedModelPositionY(self) -> float:
    #     return self.__selectedModelPositionY

    # def screenToWorld(self, screenX:np.int16, screenY:np.int16, worldPos:list) -> bool: # list of float
    #     #* Create  planes for projection plan:
    #     boundingPlanes = list(vtk.vtkPlane() for i in range(0, 4))

    #     boundingPlanes[0].SetOrigin(0.0, 1000.0, 0.0)
    #     boundingPlanes[0].SetNormal(0.0, -1.0, 0.0)

    #     boundingPlanes[1].SetOrigin(0.0, -1000.0, 0.0)
    #     boundingPlanes[1].SetNormal(0.0, 1.0, 0.0)

    #     boundingPlanes[2].SetOrigin(1000.0, 0.0, 0.0)
    #     boundingPlanes[2].SetNormal(-1.0, 0.0, 0.0)

    #     boundingPlanes[3].SetOrigin(-1000.0, 0.0, 0.0)
    #     boundingPlanes[3].SetNormal(1.0, 0.0, 0.0)

    #     #* Create projection plane parallel platform and Z coordinate from clicked position in model
    #     plane = vtk.vtkPlane()
    #     plane.SetOrigin(0.0, 0.0, self.__clickPositionZ)
    #     plane.SetNormal(0.0, 0.0, 1.0)

    #     #* Set projection and bounding planes to placer
    #     placer = vtk.vtkBoundedPlanePointPlacer()
    #     placer.SetObliquePlane(plane)
    #     placer.SetProjectionNormalToOblique()

    #     placer.AddBoundingPlane(boundingPlanes[0])
    #     placer.AddBoundingPlane(boundingPlanes[1])
    #     placer.AddBoundingPlane(boundingPlanes[2])
    #     placer.AddBoundingPlane(boundingPlanes[3])

    #     screenPos = list(0.0 for i in range(0, 2)) # 2 items
    #     worldOrient = list(0.0 for i in range(0, 9)) # 9 items

    #     screenPos[0] = screenX
    #     #*  the y-axis flip for the pickin:
    #     screenPos[1] = self.__renderer.GetSize()[1] - screenY

    #     withinBounds = placer.ComputeWorldPosition(self.__renderer, screenPos, worldPos, worldOrient) # int16_t

    #     return withinBounds

    # def resetCamera(self):
    #     #* Seting the clipping range here messes with the opacity of the actors prior to moving the camera
    #     m_camPositionX = -237.885
    #     m_camPositionY = -392.348
    #     m_camPositionZ = 369.477
    #     self.__renderer.GetActiveCamera().SetPosition(m_camPositionX, m_camPositionY, m_camPositionZ)
    #     self.__renderer.GetActiveCamera().SetFocalPoint(0.0, 0.0, 0.0)
    #     self.__renderer.GetActiveCamera().SetViewUp(0.0, 0.0, 1.0)
    #     self.__renderer.ResetCameraClippingRange()
