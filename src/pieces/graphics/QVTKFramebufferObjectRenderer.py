from PySide2.QtCore import QObject, QUrl, qDebug, qCritical, QFileInfo, QEvent, Qt, QSize, Signal
from PySide2.QtGui import QSurfaceFormat, QColor, QMouseEvent, QWheelEvent, QOpenGLFramebufferObject, QOpenGLFramebufferObjectFormat, QOpenGLFunctions
from PySide2.QtQuick import QQuickFramebufferObject

from Model import Model, setSelectedModelColor
from ProcessingEngine import ProcessingEngine

import numpy as np
import vtk
import logging
from OpenGL import GL


#* https://github.com/Kitware/VTK/blob/master/GUISupport/Qt/QVTKOpenGLNativeWidget.cxx
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
fmt.setStereo(True)
fmt.setSamples(0) # we never need multisampling in the context since the FBO can support multisamples independently

class FboRenderer(QQuickFramebufferObject.Renderer):
    def __init__(self):
        super().__init__()

        self.renderer = RendererHelper()
        self.__fbo = None

    def render( self ):
        self.renderer.render()

    def synchronize(self, item:QQuickFramebufferObject):
        self.renderer.synchronize(item)

    def createFramebufferObject( self, size ):
        self.__fbo = self.renderer.createFramebufferObject( size )
        return self.__fbo

# class RendererHelper(QObject, QQuickFramebufferObject.Renderer, QOpenGLFunctions):
class RendererHelper(QObject):
    isModelSelectedChanged = Signal(bool)
    selectedModelPositionXChanged = Signal(float)
    selectedModelPositionYChanged = Signal(float)

    def __init__(self):
        qDebug('RendererHelper::__init__()')
        super().__init__()
        self.__vtkFboItem = None
        self.gl = QOpenGLFunctions()
        self.__processingEngine:ProcessingEngine = None

        self.__selectedModel:Model = None
        self.__selectedActor:vtk.vtkActor = None
        self.__isModelSelected:bool = False

        self.__selectedModelPositionX:float = 0.0
        self.__selectedModelPositionY:float = 0.0

        self.__mouseLeftButton:QMouseEvent = None
        self.__mouseEvent:QMouseEvent = None
        self.__moveEvent:QMouseEvent = None
        # self.__wheelEvent:QWheelEvent = None

        self.__platformModel:vtk.vtkCubeSource = None
        self.__platformGrid:vtk.vtkPolyData = None
        self.__platformModelActor:vtk.vtkActor = None
        self.__platformGridActor:vtk.vtkActor = None

        self.__platformWidth:float = 200.0
        self.__platformDepth:float = 200.0
        # self.__platformHeight:float = 200.0
        self.__platformThickness:float = 2.0
        self.__gridBottomHeight:float = 0.15
        self.__gridSize:np.uint16 = 10

        # self.__camPositionX:float = 0.0
        # self.__camPositionY:float = 0.0
        # self.__camPositionZ:float = 0.0

        self.__clickPositionZ:float = 0.0

        self.__firstRender:bool = True

        self.__modelsRepresentationOption:int = 0
        self.__modelsOpacity:float = 1.0
        self.__modelsGouraudInterpolation:bool = False

        #* Renderer
        #* https://vtk.org/doc/nightly/html/classQVTKOpenGLNativeWidget.html#details
        # QSurfaceFormat.setDefaultFormat(QVTKOpenGLNativeWidget.defaultFormat()) # from vtk 8.2.0
        # QSurfaceFormat.setDefaultFormat(fmt)
        self.__vtkRenderWindow:vtk.vtkGenericOpenGLRenderWindow = vtk.vtkGenericOpenGLRenderWindow()
        self.__renderer:vtk.vtkRenderer = vtk.vtkRenderer()
        self.__vtkRenderWindow.AddRenderer(self.__renderer)

        #* Interactor
        self.__vtkRenderWindowInteractor:vtk.vtkGenericRenderWindowInteractor = vtk.vtkGenericRenderWindowInteractor()
        self.__vtkRenderWindowInteractor.EnableRenderOff()
        self.__vtkRenderWindow.SetInteractor(self.__vtkRenderWindowInteractor)

        #* Initialize the OpenGL context for the renderer
        self.__vtkRenderWindow.OpenGLInitContext()

        #* Interactor Style
        style = vtk.vtkInteractorStyleTrackballCamera()
        style.SetDefaultRenderer(self.__renderer)
        style.SetMotionFactor(10.0)
        self.__vtkRenderWindowInteractor.SetInteractorStyle(style)

        #* Picker
        self.__picker:vtk.vtkCellPicker = vtk.vtkCellPicker()
        self.__picker.SetTolerance(0.0)

    def setVtkFboItem(self, vtkFboItem):
        qDebug('RendererHelper::setVtkFboItem()')
        self.__vtkFboItem = vtkFboItem

    def setProcessingEngine(self, processingEngine:ProcessingEngine):
        qDebug('RendererHelper::setProcessingEngine()')
        self.__processingEngine = processingEngine

    def synchronize(self, item:QQuickFramebufferObject):
        # qDebug('RendererHelper::synchronize()')
        #* the first synchronize
        # if not self.__vtkFboItem:
        #     from QVTKFramebufferObjectItem import QVTKFramebufferObjectItem
        #     self.__vtkFboItem = (QVTKFramebufferObjectItem)(item)

        # if not self.__vtkFboItem.isInitialized():
        #     self.__vtkFboItem.setVtkRendererHelper(self)
        #     self.__vtkFboItem.rendererInitialized.emit()

        rendererSize = self.__vtkRenderWindow.GetSize()
        if self.__vtkFboItem.width() != rendererSize[0] or self.__vtkFboItem.height() != rendererSize[1]:
            self.__vtkRenderWindow.SetSize(int(self.__vtkFboItem.width()), int(self.__vtkFboItem.height()))

        #* Copy mouse events
        if not self.__vtkFboItem.getLastMouseLeftButton(clone=False).isAccepted():
            self.__mouseLeftButton = self.__vtkFboItem.getLastMouseLeftButton()
            self.__vtkFboItem.getLastMouseLeftButton(clone=False).accept()

        if not self.__vtkFboItem.getLastMouseButton(clone=False).isAccepted():
            self.__mouseEvent = self.__vtkFboItem.getLastMouseButton()
            self.__vtkFboItem.getLastMouseButton(clone=False).accept()

        if not self.__vtkFboItem.getLastMoveEvent(clone=False).isAccepted():
            self.__moveEvent = self.__vtkFboItem.getLastMoveEvent()
            self.__vtkFboItem.getLastMoveEvent(clone=False).accept()

        # if not self.__vtkFboItem.getLastWheelEvent().isAccepted():
        #     self.__wheelEvent = self.__vtkFboItem.getLastWheelEvent()
        #     self.__vtkFboItem.getLastWheelEvent().accept()

        #* Get extra data
        self.__modelsRepresentationOption = self.__vtkFboItem.getModelsRepresentation()
        self.__modelsOpacity = self.__vtkFboItem.getModelsOpacity()
        self.__modelsGouraudInterpolation = self.__vtkFboItem.getGourauInterpolation()
        setSelectedModelColor(QColor(self.__vtkFboItem.getModelColorR(), self.__vtkFboItem.getModelColorG(), self.__vtkFboItem.getModelColorB()))

    def render(self):
        self.__vtkRenderWindow.PushState()
        self.openGLInitState()
        self.__vtkRenderWindow.Start()

        if self.__firstRender:
            self.initScene()
            self.__firstRender = False

        #* Process camera related commands

        #* Process mouse event
        if self.__mouseEvent and not self.__mouseEvent.isAccepted():
            self.__vtkRenderWindowInteractor.SetEventInformationFlipY(
                self.__mouseEvent.x(),
                self.__mouseEvent.y(),
                1 if (self.__mouseEvent.modifiers() & Qt.ControlModifier) > 0 else 0,
                1 if (self.__mouseEvent.modifiers() & Qt.ShiftModifier) > 0 else 0,
                '0',
                1 if self.__mouseEvent.type() == QEvent.MouseButtonDblClick else 0
            )

            if self.__mouseEvent.type() == QEvent.MouseButtonPress:
                self.__vtkRenderWindowInteractor.InvokeEvent(vtk.vtkCommand.LeftButtonPressEvent)
            elif self.__mouseEvent.type() == QEvent.MouseButtonRelease:
                self.__vtkRenderWindowInteractor.InvokeEvent(vtk.vtkCommand.LeftButtonReleaseEvent)

            self.__mouseEvent.accept()

        #* Process move event
        if self.__moveEvent and not self.__moveEvent.isAccepted():
            if self.__moveEvent.type() == QEvent.MouseMove and self.__moveEvent.buttons() & Qt.RightButton:
                self.__vtkRenderWindowInteractor.SetEventInformationFlipY(
                    self.__moveEvent.x(),
                    self.__moveEvent.y(),
                    1 if (self.__moveEvent.modifiers() & Qt.ControlModifier) > 0 else 0,
                    1 if (self.__moveEvent.modifiers() & Qt.ShiftModifier) > 0 else 0,
                    '0',
                    1 if self.__moveEvent.type() == QEvent.MouseButtonDblClick else 0
                )

                self.__vtkRenderWindowInteractor.InvokeEvent(vtk.vtkCommand.MouseMoveEvent)

            self.__moveEvent.accept()

        # #* Process wheel event
        # if self.__wheelEvent and not self.__wheelEvent.isAccepted():
        #     if self.__wheelEvent.delta() > 0:
        #         self.__vtkRenderWindowInteractor.InvokeEvent(vtk.vtkCommand.MouseWheelForwardEvent, self.__wheelEvent)
        #     elif self.__wheelEvent.delta() < 0:
        #         self.__vtkRenderWindowInteractor.InvokeEvent(vtk.vtkCommand.MouseWheelBackwardEvent, self.__wheelEvent)

        #     self.__wheelEvent.accept()

        #* Process model related commands

        #* Select model
        if self.__mouseLeftButton and not self.__mouseLeftButton.isAccepted():
            self.__selectModel(self.__mouseLeftButton.x(), self.__mouseLeftButton.y())
            self.__mouseLeftButton.accept()

        #* Model transformations

        command = None # CommandModel
        while not self.__vtkFboItem.isCommandsQueueEmpty():
            self.__vtkFboItem.lockCommandsQueueMutex()

            command = self.__vtkFboItem.getCommandsQueueFront()
            if not command.isReady():
                self.__vtkFboItem.unlockCommandsQueueMutex()
                break
            self.__vtkFboItem.commandsQueuePop()

            self.__vtkFboItem.unlockCommandsQueueMutex()

            command.execute()

        #* Reset the view-up vector. self improves the interaction of the camera with the plate.
        self.__renderer.GetActiveCamera().SetViewUp(0.0, 0.0, 1.0)

        #* Extra actions
        self.__processingEngine.setModelsRepresentation(self.__modelsRepresentationOption)
        self.__processingEngine.setModelsOpacity(self.__modelsOpacity)
        self.__processingEngine.setModelsGouraudInterpolation(self.__modelsGouraudInterpolation)
        self.__processingEngine.updateModelsColor()

        #* Render
        self.__vtkRenderWindow.Render()
        self.__vtkRenderWindow.PopState()

        self.__vtkFboItem.window().resetOpenGLState()

    def openGLInitState(self):
        self.__vtkRenderWindow.OpenGLInitState()
        self.__vtkRenderWindow.MakeCurrent()
        self.gl.initializeOpenGLFunctions()
        self.gl.glUseProgram(0)

    def createFramebufferObject(self, size:QSize) -> QOpenGLFramebufferObject:
        qDebug('RendererHelper::createFramebufferObject()')
        macSize = QSize(size.width() / 2, size.height() / 2)

        format = QOpenGLFramebufferObjectFormat()
        format.setAttachment(QOpenGLFramebufferObject.Depth)

    # ifdef Q_OS_MAC
    #     std::unique_ptr<QOpenGLFramebufferObject> framebufferObject(new QOpenGLFramebufferObject(macSize, format))
    # else
        framebufferObject = QOpenGLFramebufferObject(size, format)
    # endif
        self.__vtkRenderWindow.SetBackLeftBuffer(GL.GL_COLOR_ATTACHMENT0)
        self.__vtkRenderWindow.SetFrontLeftBuffer(GL.GL_COLOR_ATTACHMENT0)
        self.__vtkRenderWindow.SetBackBuffer(GL.GL_COLOR_ATTACHMENT0)
        self.__vtkRenderWindow.SetFrontBuffer(GL.GL_COLOR_ATTACHMENT0)
        self.__vtkRenderWindow.SetSize(framebufferObject.size().width(), framebufferObject.size().height())
        self.__vtkRenderWindow.SetOffScreenRendering(True)
        self.__vtkRenderWindow.Modified()
        framebufferObject.release()
        return framebufferObject

    def initScene(self):
        qDebug('RendererHelper::initScene()')

        self.__vtkRenderWindow.SetOffScreenRendering(True)

        #* Top background color
        r2 = 245.0 / 255.0
        g2 = 245.0 / 255.0
        b2 = 245.0 / 255.0

        #* Bottom background color
        r1 = 170.0 / 255.0
        g1 = 170.0 / 255.0
        b1 = 170.0 / 255.0

        self.__renderer.SetBackground(r2, g2, b2)
        self.__renderer.SetBackground2(r1, g1, b1)
        self.__renderer.GradientBackgroundOn()

        # #* Axes
        axes = vtk.vtkAxesActor()
        axes_length = 20.0
        axes_label_font_size = np.int16(20)
        axes.SetTotalLength(axes_length, axes_length, axes_length)
        axes.GetXAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        axes.GetYAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        axes.GetZAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(axes_label_font_size)
        axes.GetYAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(axes_label_font_size)
        axes.GetZAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(axes_label_font_size)
        self.__renderer.AddActor(axes)

        # #* Platform
        self.__generatePlatform()

        #* Initial camera position
        self.resetCamera()

    def __generatePlatform(self):
        qDebug('RendererHelper::__generatePlatform()')

        #* Platform Model
        platformModelMapper = vtk.vtkPolyDataMapper()

        self.__platformModel = vtk.vtkCubeSource()
        platformModelMapper.SetInputConnection(self.__platformModel.GetOutputPort())

        self.__platformModelActor = vtk.vtkActor()
        self.__platformModelActor.SetMapper(platformModelMapper)
        self.__platformModelActor.GetProperty().SetColor(1, 1, 1)
        self.__platformModelActor.GetProperty().LightingOn()
        self.__platformModelActor.GetProperty().SetOpacity(1)
        self.__platformModelActor.GetProperty().SetAmbient(0.45)
        self.__platformModelActor.GetProperty().SetDiffuse(0.4)

        self.__platformModelActor.PickableOff()
        self.__renderer.AddActor(self.__platformModelActor)

        #* Platform Grid
        self.__platformGrid = vtk.vtkPolyData()

        platformGridMapper = vtk.vtkPolyDataMapper()
        platformGridMapper.SetInputData(self.__platformGrid)

        self.__platformGridActor = vtk.vtkActor()
        self.__platformGridActor.SetMapper(platformGridMapper)
        self.__platformGridActor.GetProperty().LightingOff()
        self.__platformGridActor.GetProperty().SetColor(0.45, 0.45, 0.45)
        self.__platformGridActor.GetProperty().SetOpacity(1)
        self.__platformGridActor.PickableOff()
        self.__renderer.AddActor(self.__platformGridActor)

        self.__updatePlatform()

    def __updatePlatform(self):
        qDebug('RendererHelper::__updatePlatform()')

        #* Platform Model

        if self.__platformModel:
            self.__platformModel.SetXLength(self.__platformWidth)
            self.__platformModel.SetYLength(self.__platformDepth)
            self.__platformModel.SetZLength(self.__platformThickness)
            self.__platformModel.SetCenter(0.0, 0.0, -self.__platformThickness / 2)

        #* Platform Grid
        gridPoints = vtk.vtkPoints()
        gridCells = vtk.vtkCellArray()

        i = -self.__platformWidth / 2
        while i <= self.__platformWidth / 2:
            self.__createLine(i, -self.__platformDepth / 2, self.__gridBottomHeight, i, self.__platformDepth / 2, self.__gridBottomHeight, gridPoints, gridCells)
            i += self.__gridSize

        i = -self.__platformDepth / 2
        while i <= self.__platformDepth / 2:
            self.__createLine(-self.__platformWidth / 2, i, self.__gridBottomHeight, self.__platformWidth / 2, i, self.__gridBottomHeight, gridPoints, gridCells)
            i += self.__gridSize

        self.__platformGrid.SetPoints(gridPoints)
        self.__platformGrid.SetLines(gridCells)

    def __createLine(self, x1:float, y1:float, z1:float, x2:float, y2:float, z2:float, points:vtk.vtkPoints, cells:vtk.vtkCellArray):
        line = vtk.vtkPolyLine()
        line.GetPointIds().SetNumberOfIds(2)

        id_1 = points.InsertNextPoint(x1, y1, z1) # vtkIdType
        id_2 = points.InsertNextPoint(x2, y2, z2) # vtkIdType

        line.GetPointIds().SetId(0, id_1)
        line.GetPointIds().SetId(1, id_2)

        cells.InsertNextCell(line)

    def addModelActor(self, model:Model):
        self.__renderer.AddActor(model.getModelActor())
        # qDebug(f'RendererHelper::addModelActor(): Model added {model}')

    def __selectModel(self, x:np.int16, y:np.int16):
        qDebug('RendererHelper::__selectModel()')

        #*  the y-axis flip for the pickin:
        self.__picker.Pick(x, self.__renderer.GetSize()[1] - y, 0, self.__renderer)

        #* Get pick position
        # clickPosition = [0.0, 0.0, 0.0]
        # self.__picker.GetPickPosition(clickPosition)
        clickPosition = self.__picker.GetPickPosition()
        self.__clickPositionZ = clickPosition[2]

        if self.__selectedActor == self.__picker.GetActor():
            if self.__selectedModel:
                self.__selectedModel.setMouseDeltaXY(clickPosition[0] - self.__selectedModel.getPositionX(), clickPosition[1] - self.__selectedModel.getPositionY())
            return

        #* Disconnect signals
        if self.__selectedModel:
            self.__clearSelectedModel()

        #* Pick the new actor
        self.__selectedActor = self.__picker.GetActor()

        self.__selectedModel = self.__getSelectedModelNoLock()

        if self.__selectedActor:
            # qDebug(f'RendererHelper::__selectModel(): picked actor {self.__selectedActor}')

            self.__selectedModel.setSelected(True)

            #* Connect signals
            self.__selectedModel.positionXChanged.connect(self.setSelectedModelPositionX)
            self.__selectedModel.positionYChanged.connect(self.setSelectedModelPositionY)

            self.setSelectedModelPositionX(self.__selectedModel.getPositionX())
            self.setSelectedModelPositionY(self.__selectedModel.getPositionY())

            self.__setIsModelSelected(True)

            #* Set mouse click delta from center position
            self.__selectedModel.setMouseDeltaXY(clickPosition[0] - self.__selectedModel.getPositionX(), clickPosition[1] - self.__selectedModel.getPositionY())
        else:
            self.__setIsModelSelected(False)

        qDebug('RendererHelper::__selectModel() end')

    def __clearSelectedModel(self):
        self.__selectedModel.setSelected(False)

        self.__selectedModel.positionXChanged.disconnect(self.setSelectedModelPositionX)
        self.__selectedModel.positionYChanged.disconnect(self.setSelectedModelPositionY)

        self.__selectedModel = None
        self.__selectedActor = None

    def __setIsModelSelected(self, isModelSelected:bool):
        if self.__isModelSelected != isModelSelected:
            qDebug(f'RendererHelper::__setIsModelSelected(): {isModelSelected}')
            self.__isModelSelected = isModelSelected
            self.isModelSelectedChanged.emit(isModelSelected)

    def isModelSelected(self) -> bool:
        return self.__isModelSelected

    def getSelectedModel(self) -> Model:
        selectedModel = self.__getSelectedModelNoLock()
        return selectedModel

    def __getSelectedModelNoLock(self) -> Model:
        return self.__processingEngine.getModelFromActor(self.__selectedActor)

    def setSelectedModelPositionX(self, positionX:float):
        if self.__selectedModelPositionX != positionX:
            self.__selectedModelPositionX = positionX
            self.selectedModelPositionXChanged.emit(positionX)

    def setSelectedModelPositionY(self, positionY:float):
        if self.__selectedModelPositionY != positionY:
            self.__selectedModelPositionY = positionY
            self.selectedModelPositionYChanged.emit(positionY)

    def getSelectedModelPositionX(self) -> float:
        return self.__selectedModelPositionX

    def getSelectedModelPositionY(self) -> float:
        return self.__selectedModelPositionY

    def screenToWorld(self, screenX:np.int16, screenY:np.int16, worldPos:list) -> bool: # list of float
        #* Create  planes for projection plan:
        boundingPlanes = list(vtk.vtkPlane() for i in range(0, 4))

        boundingPlanes[0].SetOrigin(0.0, 1000.0, 0.0)
        boundingPlanes[0].SetNormal(0.0, -1.0, 0.0)

        boundingPlanes[1].SetOrigin(0.0, -1000.0, 0.0)
        boundingPlanes[1].SetNormal(0.0, 1.0, 0.0)

        boundingPlanes[2].SetOrigin(1000.0, 0.0, 0.0)
        boundingPlanes[2].SetNormal(-1.0, 0.0, 0.0)

        boundingPlanes[3].SetOrigin(-1000.0, 0.0, 0.0)
        boundingPlanes[3].SetNormal(1.0, 0.0, 0.0)

        #* Create projection plane parallel platform and Z coordinate from clicked position in model
        plane = vtk.vtkPlane()
        plane.SetOrigin(0.0, 0.0, self.__clickPositionZ)
        plane.SetNormal(0.0, 0.0, 1.0)

        #* Set projection and bounding planes to placer
        placer = vtk.vtkBoundedPlanePointPlacer()
        placer.SetObliquePlane(plane)
        placer.SetProjectionNormalToOblique()

        placer.AddBoundingPlane(boundingPlanes[0])
        placer.AddBoundingPlane(boundingPlanes[1])
        placer.AddBoundingPlane(boundingPlanes[2])
        placer.AddBoundingPlane(boundingPlanes[3])

        screenPos = list(0.0 for i in range(0, 2)) # 2 items
        worldOrient = list(0.0 for i in range(0, 9)) # 9 items

        screenPos[0] = screenX
        #*  the y-axis flip for the pickin:
        screenPos[1] = self.__renderer.GetSize()[1] - screenY

        withinBounds = placer.ComputeWorldPosition(self.__renderer, screenPos, worldPos, worldOrient) # int16_t

        return withinBounds

    def resetCamera(self):
        #* Seting the clipping range here messes with the opacity of the actors prior to moving the camera
        m_camPositionX = -237.885
        m_camPositionY = -392.348
        m_camPositionZ = 369.477
        self.__renderer.GetActiveCamera().SetPosition(m_camPositionX, m_camPositionY, m_camPositionZ)
        self.__renderer.GetActiveCamera().SetFocalPoint(0.0, 0.0, 0.0)
        self.__renderer.GetActiveCamera().SetViewUp(0.0, 0.0, 1.0)
        self.__renderer.ResetCameraClippingRange()
