from PySide2.QtCore import QObject, QUrl, qDebug, qCritical, QFileInfo, QEvent, Qt, QSize, Signal
from PySide2.QtGui import QSurfaceFormat, QColor, QMouseEvent, QWheelEvent, QOpenGLFramebufferObject, QOpenGLFramebufferObjectFormat, QOpenGLFunctions
from PySide2.QtQuick import QQuickFramebufferObject
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from Model import Model, setSelectedModelColor
from ProcessingEngine import ProcessingEngine

import numpy as np
import vtk

# from vtk.qt.QVTKRenderWindowInteractor import QV

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
fmt.setStereo(False)
fmt.setSamples(0) # we never need multisampling in the context since the FBO can support multisamples independently

class QVTKFramebufferObjectRenderer(QObject, QQuickFramebufferObject.Renderer, QOpenGLFunctions):
    isModelSelectedChanged = Signal()
    selectedModelPositionXChanged = Signal()
    selectedModelPositionYChanged = Signal()

    def __init__(self):
        super().__init__()
        self.__m_processingEngine:ProcessingEngine = None
        from QVTKFramebufferObjectItem import QVTKFramebufferObjectItem
        self.__m_vtkFboItem:QVTKFramebufferObjectItem = None

        self.__m_selectedModel:Model = None
        self.__m_selectedActor:vtkActor = None
        self.__m_isModelSelected:bool = False

        self.__m_selectedModelPositionX:float = 0.0
        self.__m_selectedModelPositionY:float = 0.0

        self.__m_mouseLeftButton:QMouseEvent = None
        self.__m_mouseEvent:QMouseEvent = None
        self.__m_moveEvent:QMouseEvent = None
        self.__m_wheelEvent:QWheelEvent = None

        self.__m_platformModel:vtkCubeSource = None
        self.__m_platformGrid:vtkPolyData = None
        self.__m_platformModelActor:vtkActor = None
        self.__m_platformGridActor:vtkActor = None

        self.__m_platformWidth:float = 200.0
        self.__m_platformDepth:float = 200.0
        self.__m_platformHeight:float = 200.0
        self.__m_platformThickness:float = 2.0
        self.__m_gridBottomHeight:float = 0.15
        self.__m_gridSize:np.uint16 = 10

        self.__m_camPositionX:float = 0.0
        self.__m_camPositionY:float = 0.0
        self.__m_camPositionZ:float = 0.0

        self.__m_clickPositionZ:float = 0.0

        self.__m_firstRender:bool = True

        self.__m_modelsRepresentationOption:int = 0
        self.__m_modelsOpacity:float = 1.0
        self.__m_modelsGouraudInterpolation:bool = False

        #* Renderer
        #* https://vtk.org/doc/nightly/html/classQVTKOpenGLNativeWidget.html#details
        # QSurfaceFormat.setDefaultFormat(QVTKOpenGLNativeWidget.defaultFormat()) # from vtk 8.2.0
        QSurfaceFormat.setDefaultFormat(fmt)
        self.__m_vtkRenderWindow:vtkGenericOpenGLRenderWindow = vtk.vtkGenericOpenGLRenderWindow()
        self.__m_renderer:vtkRenderer = vtk.vtkRenderer()
        self.__m_vtkRenderWindow.AddRenderer(self.__m_renderer)

        #* Interactor
        self.__m_vtkRenderWindowInteractor:vtk.vtkGenericRenderWindowInteractor = vtk.vtkGenericRenderWindowInteractor()
        self.__m_vtkRenderWindowInteractor.EnableRenderOff()
        self.__m_vtkRenderWindow.SetInteractor(self.__m_vtkRenderWindowInteractor)

        #* Initialize the OpenGL context for the renderer
        self.__m_vtkRenderWindow.OpenGLInitContext()

        #* Interactor Style
        style = vtk.vtkInteractorStyleTrackballCamera()
        style.SetDefaultRenderer(self.__m_renderer)
        style.SetMotionFactor(10.0)
        self.__m_vtkRenderWindowInteractor.SetInteractorStyle(style)

        #* Picker
        self.__m_picker:vtkCellPicker = vtk.vtkCellPicker()
        self.__m_picker.SetTolerance(0.0)

        self.update()

    def setProcessingEngine(self, processingEngine:ProcessingEngine):
        self.__m_processingEngine = processingEngine

    def synchronize(self, item:QQuickFramebufferObject):
        qDebug('QVTKFramebufferObjectRenderer::synchronize()')
        #* the first synchronize
        if not self.__m_vtkFboItem:
            from QVTKFramebufferObjectItem import QVTKFramebufferObjectItem
            self.__m_vtkFboItem = (QVTKFramebufferObjectItem)(item)

        if not self.__m_vtkFboItem.isInitialized():
            self.__m_vtkFboItem.setVtkFboRenderer(self)
            self.__m_vtkFboItem.rendererInitialized.emit()

        rendererSize = self.__m_vtkRenderWindow.GetSize()

        if self.__m_vtkFboItem.width() != rendererSize[0] or self.__m_vtkFboItem.height() != rendererSize[1]:
            self.__m_vtkRenderWindow.SetSize(self.__m_vtkFboItem.width(), self.__m_vtkFboItem.height())

        #* Copy mouse events
        if not self.__m_vtkFboItem.getLastMouseLeftButton().isAccepted():
            self.__m_mouseLeftButton = self.__m_vtkFboItem.getLastMouseLeftButton()
            self.__m_vtkFboItem.getLastMouseLeftButton().accept()

        if not self.__m_vtkFboItem.getLastMouseButton().isAccepted():
            self.__m_mouseEvent = self.__m_vtkFboItem.getLastMouseButton()
            self.__m_vtkFboItem.getLastMouseButton().accept()

        if not self.__m_vtkFboItem.getLastMoveEvent().isAccepted():
            self.__m_moveEvent = self.__m_vtkFboItem.getLastMoveEvent()
            self.__m_vtkFboItem.getLastMoveEvent().accept()

        if not self.__m_vtkFboItem.getLastWheelEvent().isAccepted():
            self.__m_wheelEvent = self.__m_vtkFboItem.getLastWheelEvent()
            self.__m_vtkFboItem.getLastWheelEvent().accept()

        #* Get extra data
        self.__m_modelsRepresentationOption = self.__m_vtkFboItem.getModelsRepresentation()
        self.__m_modelsOpacity = self.__m_vtkFboItem.getModelsOpacity()
        self.__m_modelsGouraudInterpolation = self.__m_vtkFboItem.getGourauInterpolation()
        setSelectedModelColor(QColor(self.__m_vtkFboItem.getModelColorR(), self.__m_vtkFboItem.getModelColorG(), self.__m_vtkFboItem.getModelColorB()))

    def render(self):
        qDebug('QVTKFramebufferObjectRenderer::render()')
        self.__m_vtkRenderWindow.PushState()
        self.openGLInitState()
        self.__m_vtkRenderWindow.Start()

        if self.__m_firstRender:
            self.initScene()
            self.__m_firstRender = False

        #* Process camera related commands

        #* Process mouse event
        if self.__m_mouseEvent and not self.__m_mouseEvent.isAccepted():
            self.__m_vtkRenderWindowInteractor.SetEventInformationFlipY(self.__m_mouseEvent.x(), self.__m_mouseEvent.y(),
                                                                1 if (self.__m_mouseEvent.modifiers() & Qt.ControlModifier) > 0 else 0,
                                                                1 if (self.__m_mouseEvent.modifiers() & Qt.ShiftModifier) > 0 else 0, 0,
                                                                1 if self.__m_mouseEvent.type() == QEvent.MouseButtonDblClick else 0)

            if self.__m_mouseEvent.type() == QEvent.MouseButtonPress:
                self.__m_vtkRenderWindowInteractor.InvokeEvent(vtk.vtkCommand.LeftButtonPressEvent, self.__m_mouseEvent.get())
            elif self.__m_mouseEvent.type() == QEvent.MouseButtonRelease:
                self.__m_vtkRenderWindowInteractor.InvokeEvent(vtk.vtkCommand.LeftButtonReleaseEvent, self.__m_mouseEvent.get())

            self.__m_mouseEvent.accept()

        #* Process move event
        if self.__m_moveEvent and not self.__m_moveEvent.isAccepted():
            if self.__m_moveEvent.type() == QEvent.MouseMove and self.__m_moveEvent.buttons() & Qt.RightButton:
                self.__m_vtkRenderWindowInteractor.SetEventInformationFlipY(self.__m_moveEvent.x(), self.__m_moveEvent.y(),
                                                                    1 if (self.__m_moveEvent.modifiers() & Qt.ControlModifier) > 0 else 0,
                                                                    1 if (self.__m_moveEvent.modifiers() & Qt.ShiftModifier) > 0 else 0, 0,
                                                                    1 if self.__m_moveEvent.type() == QEvent.MouseButtonDblClick else 0)

                self.__m_vtkRenderWindowInteractor.InvokeEvent(vtk.vtkCommand.MouseMoveEvent, self.__m_moveEvent.get())

            self.__m_moveEvent.accept()

        #* Process wheel event
        if self.__m_wheelEvent and not self.__m_wheelEvent.isAccepted():
            if self.__m_wheelEvent.delta() > 0:
                self.__m_vtkRenderWindowInteractor.InvokeEvent(vtk.vtkCommand.MouseWheelForwardEvent, self.__m_wheelEvent.get())
            elif self.__m_wheelEvent.delta() < 0:
                self.__m_vtkRenderWindowInteractor.InvokeEvent(vtk.vtkCommand.MouseWheelBackwardEvent, self.__m_wheelEvent.get())

            self.__m_wheelEvent.accept()

        #* Process model related commands

        #* Select model

        if self.__m_mouseLeftButton and not self.__m_mouseLeftButton.isAccepted():
            self.__selectModel(self.__m_mouseLeftButton.x(), self.__m_mouseLeftButton.y())
            self.__m_mouseLeftButton.accept()

        #* Model transformations

        command = None # CommandModel
        while not self.__m_vtkFboItem.isCommandsQueueEmpty():
            self.__m_vtkFboItem.lockCommandsQueueMutex()

            command = self.__m_vtkFboItem.getCommandsQueueFront()
            if not command.isReady():
                self.__m_vtkFboItem.unlockCommandsQueueMutex()
                break
            self.__m_vtkFboItem.commandsQueuePop()

            self.__m_vtkFboItem.unlockCommandsQueueMutex()

            command.execute()

        #* Reset the view-up vector. self improves the interaction of the camera with the plate.
        self.__m_renderer.GetActiveCamera().SetViewUp(0.0, 0.0, 1.0)

        #* Extra actions
        self.__m_processingEngine.setModelsRepresentation(self.__m_modelsRepresentationOption)
        self.__m_processingEngine.setModelsOpacity(self.__m_modelsOpacity)
        self.__m_processingEngine.setModelsGouraudInterpolation(self.__m_modelsGouraudInterpolation)
        self.__m_processingEngine.updateModelsColor()

        #* Render
        self.__m_vtkRenderWindow.Render()
        self.__m_vtkRenderWindow.PopState()

        self.__m_vtkFboItem.window().resetOpenGLState()

    def openGLInitState(self):
        self.__m_vtkRenderWindow.OpenGLInitState()
        self.__m_vtkRenderWindow.MakeCurrent()
        QOpenGLFunctions.initializeOpenGLFunctions()
        QOpenGLFunctions.glUseProgram(0)

    def createFramebufferObject(self, size:QSize) -> QOpenGLFramebufferObject:
        qDebug('QVTKFramebufferObjectRenderer::createFramebufferObject()')
        macSize = QSize(size.width() / 2, size.height() / 2)

        format = QOpenGLFramebufferObjectFormat()
        format.setAttachment(QOpenGLFramebufferObject.Depth)

    # ifdef Q_OS_MAC
    #     std::unique_ptr<QOpenGLFramebufferObject> framebufferObject(new QOpenGLFramebufferObject(macSize, format))
    # else
        framebufferObject = QOpenGLFramebufferObject(size, format)
    # endif
        self.__m_vtkRenderWindow.SetBackLeftBuffer(GL_COLOR_ATTACHMENT0)
        self.__m_vtkRenderWindow.SetFrontLeftBuffer(GL_COLOR_ATTACHMENT0)
        self.__m_vtkRenderWindow.SetBackBuffer(GL_COLOR_ATTACHMENT0)
        self.__m_vtkRenderWindow.SetFrontBuffer(GL_COLOR_ATTACHMENT0)
        self.__m_vtkRenderWindow.SetSize(framebufferObject.size().width(), framebufferObject.size().height())
        self.__m_vtkRenderWindow.SetOffScreenRendering(True)
        self.__m_vtkRenderWindow.Modified()

        return framebufferObject.release()

    def initScene(self):
        qDebug('QVTKFramebufferObjectRenderer::initScene()')

        self.__m_vtkRenderWindow.SetOffScreenRendering(True)

        #* Top background color
        r2 = 245.0 / 255.0
        g2 = 245.0 / 255.0
        b2 = 245.0 / 255.0

        #* Bottom background color
        r1 = 170.0 / 255.0
        g1 = 170.0 / 255.0
        b1 = 170.0 / 255.0

        self.__m_renderer.SetBackground(r2, g2, b2)
        self.__m_renderer.SetBackground2(r1, g1, b1)
        self.__m_renderer.GradientBackgroundOn()

        #* Axes
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
        self.__m_renderer.AddActor(axes)

        #* Platform
        self.__generatePlatform()

        #* Initial camera position
        self.resetCamera()

    def __generatePlatform(self):
        qDebug('QVTKFramebufferObjectRenderer::__generatePlatform()')

        #* Platform Model
        platformModelMapper = vtk.vtkPolyDataMapper()

        self.__m_platformModel = vtk.vtkCubeSource()
        platformModelMapper.SetInputConnection(self.__m_platformModel.GetOutputPort())

        self.__m_platformModelActor = vtk.vtkActor()
        self.__m_platformModelActor.SetMapper(platformModelMapper)
        self.__m_platformModelActor.GetProperty().SetColor(1, 1, 1)
        self.__m_platformModelActor.GetProperty().LightingOn()
        self.__m_platformModelActor.GetProperty().SetOpacity(1)
        self.__m_platformModelActor.GetProperty().SetAmbient(0.45)
        self.__m_platformModelActor.GetProperty().SetDiffuse(0.4)

        self.__m_platformModelActor.PickableOff()
        self.__m_renderer.AddActor(self.__m_platformModelActor)

        #* Platform Grid
        self.__m_platformGrid = vtk.vtkPolyData()

        platformGridMapper = vtk.vtkPolyDataMapper()
        platformGridMapper.SetInputData(self.__m_platformGrid)

        self.__m_platformGridActor = vtk.vtkActor()
        self.__m_platformGridActor.SetMapper(platformGridMapper)
        self.__m_platformGridActor.GetProperty().LightingOff()
        self.__m_platformGridActor.GetProperty().SetColor(0.45, 0.45, 0.45)
        self.__m_platformGridActor.GetProperty().SetOpacity(1)
        self.__m_platformGridActor.PickableOff()
        self.__m_renderer.AddActor(self.__m_platformGridActor)

        self.__updatePlatform()

    def __updatePlatform(self):
        qDebug('QVTKFramebufferObjectRenderer::__updatePlatform()')

        #* Platform Model

        if self.__m_platformModel:
            self.__m_platformModel.SetXLength(self.__m_platformWidth)
            self.__m_platformModel.SetYLength(self.__m_platformDepth)
            self.__m_platformModel.SetZLength(self.__m_platformThickness)
            self.__m_platformModel.SetCenter(0.0, 0.0, -self.__m_platformThickness / 2)

        #* Platform Grid
        gridPoints = vtk.vtkPoints()
        gridCells = vtk.vtkCellArray()

        i = -self.__m_platformWidth / 2
        while i <= self.__m_platformWidth / 2:
            self.__createLine(i, -self.__m_platformDepth / 2, self.__m_gridBottomHeight, i, self.__m_platformDepth / 2, self.__m_gridBottomHeight, gridPoints, gridCells)
            i += self.__m_gridSize

        i = -self.__m_platformDepth / 2
        while i <= self.__m_platformDepth / 2:
            self.__createLine(-self.__m_platformWidth / 2, i, self.__m_gridBottomHeight, self.__m_platformWidth / 2, i, self.__m_gridBottomHeight, gridPoints, gridCells)
            i += self.__m_gridSize

        self.__m_platformGrid.SetPoints(gridPoints)
        self.__m_platformGrid.SetLines(gridCells)

    def __createLine(self, x1:float, y1:float, z1:float, x2:float, y2:float, z2:float, points:vtk.vtkPoints, cells:vtk.vtkCellArray):
        line = vtk.vtkPolyLine()
        line.GetPointIds().SetNumberOfIds(2)

        id_1 = points.InsertNextPoint(x1, y1, z1) # vtkIdType
        id_2 = points.InsertNextPoint(x2, y2, z2) # vtkIdType

        line.GetPointIds().SetId(0, id_1)
        line.GetPointIds().SetId(1, id_2)

        cells.InsertNextCell(line)

    def addModelActor(self, model:Model):
        self.__m_renderer.AddActor(model.getModelActor())

        qDebug(f'QVTKFramebufferObjectRenderer::addModelActor(): Model added {model.get()}')

    def __selectModel(self, x:np.int16, y:np.int16):
        qDebug('QVTKFramebufferObjectRenderer::__selectModel()')

        #*  the y-axis flip for the pickin:
        self.__m_picker.Pick(x, self.__m_renderer.GetSize()[1] - y, 0, self.__m_renderer)

        #* Get pick position
        clickPosition = [0.0, 0.0, 0.0]
        self.__m_picker.GetPickPosition(clickPosition)
        self.__m_clickPositionZ = clickPosition[2]

        if self.__m_selectedActor == self.__m_picker.GetActor():
            if self.__m_selectedModel:
                self.__m_selectedModel.setMouseDeltaXY(clickPosition[0] - self.__m_selectedModel.getPositionX(), clickPosition[1] - self.__m_selectedModel.getPositionY())
            return

        #* Disconnect signals
        if self.__m_selectedModel:
            self.__clearSelectedModel()

        #* Pick the new actor
        self.__m_selectedActor = self.__m_picker.GetActor()

        self.__m_selectedModel = self.__getSelectedModelNoLock()

        if self.__m_selectedActor:
            qDebug(f'QVTKFramebufferObjectRenderer::__selectModel(): picked actor {self.__m_selectedActor}')

            self.__m_selectedModel.setSelected(True)

            #* Connect signals
            self.__m_selectedModel.get().positionXChanged.connect(self.setSelectedModelPositionX)
            self.__m_selectedModel.get().positionYChanged.connect(self.setSelectedModelPositionY)

            self.setSelectedModelPositionX(self.__m_selectedModel.getPositionX())
            self.setSelectedModelPositionY(self.__m_selectedModel.getPositionY())

            self.__setIsModelSelected(True)

            #* Set mouse click delta from center position
            self.__m_selectedModel.setMouseDeltaXY(clickPosition[0] - self.__m_selectedModel.getPositionX(), clickPosition[1] - self.__m_selectedModel.getPositionY())
        else:
            self.__setIsModelSelected(False)

        qDebug('QVTKFramebufferObjectRenderer::__selectModel() end')

    def __clearSelectedModel(self):
        self.__m_selectedModel.setSelected(False)

        self.__m_selectedModel.get().positionXChanged.disconnect(self.setSelectedModelPositionX)
        self.__m_selectedModel.get().positionYChanged.disconnect(self.setSelectedModelPositionY)

        self.__m_selectedModel = None
        self.__m_selectedActor = None

    def __setIsModelSelected(self, isModelSelected:bool):
        if self.__m_isModelSelected != isModelSelected:
            qDebug(f'QVTKFramebufferObjectRenderer::__setIsModelSelected(): {isModelSelected}')
            self.__m_isModelSelected = isModelSelected
            self.isModelSelectedChanged.emit()

    def isModelSelected(self) -> bool:
        return self.__m_isModelSelected

    def getSelectedModel(self) -> Model:
        selectedModel = self.__getSelectedModelNoLock()
        return selectedModel

    def __getSelectedModelNoLock(self) -> Model:
        return self.__m_processingEngine.getModelFromActor(self.__m_selectedActor)

    def setSelectedModelPositionX(self, positionX:float):
        if self.__m_selectedModelPositionX != positionX:
            self.__m_selectedModelPositionX = positionX
            self.selectedModelPositionXChanged.emit()

    def setSelectedModelPositionY(self, positionY:float):
        if self.__m_selectedModelPositionY != positionY:
            self.__m_selectedModelPositionY = positionY
            self.selectedModelPositionYChanged.emit()

    def getSelectedModelPositionX(self) -> float:
        return self.__m_selectedModelPositionX

    def getSelectedModelPositionY(self) -> float:
        return self.__m_selectedModelPositionY

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
        plane.SetOrigin(0.0, 0.0, self.__m_clickPositionZ)
        plane.SetNormal(0.0, 0.0, 1.0)

        #* Set projection and bounding planes to placer
        placer = vtk.vtkBoundedPlanePointPlacer()
        placer.SetObliquePlane(plane)
        placer.SetProjectionNormalToOblique()

        placer.AddBoundingPlane(boundingPlanes[0].Get())
        placer.AddBoundingPlane(boundingPlanes[1].Get())
        placer.AddBoundingPlane(boundingPlanes[2].Get())
        placer.AddBoundingPlane(boundingPlanes[3].Get())

        screenPos = list(0.0 for i in range(0, 2)) # 2 items
        worldOrient = list(0.0 for i in range(0, 9)) # 9 items

        screenPos[0] = screenX
        #*  the y-axis flip for the pickin:
        screenPos[1] = self.__m_renderer.GetSize()[1] - screenY

        withinBounds = placer.ComputeWorldPosition(self.__m_renderer, screenPos, worldPos, worldOrient) # int16_t

        return withinBounds

    def resetCamera(self):
        #* Seting the clipping range here messes with the opacity of the actors prior to moving the camera
        m_camPositionX = -237.885
        m_camPositionY = -392.348
        m_camPositionZ = 369.477
        self.__m_renderer.GetActiveCamera().SetPosition(m_camPositionX, m_camPositionY, m_camPositionZ)
        self.__m_renderer.GetActiveCamera().SetFocalPoint(0.0, 0.0, 0.0)
        self.__m_renderer.GetActiveCamera().SetViewUp(0.0, 0.0, 1.0)
        self.__m_renderer.ResetCameraClippingRange()
