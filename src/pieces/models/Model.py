from PySide2.QtCore import QObject, QUrl, qDebug, qCritical, QFileInfo, Signal
from PySide2.QtGui import QColor
import threading
import vtk

m_defaultModelColor:QColor = QColor("#0277bd")
m_selectedModelColor:QColor = QColor("#03a9f4")

def setSelectedModelColor(selectedModelColor:QColor):
    global m_selectedModelColor
    m_selectedModelColor = selectedModelColor

class Model(QObject):
    positionXChanged = Signal(float)
    positionYChanged = Signal(float)

    def __init__(self, modelData:vtk.vtkPolyData):
        super().__init__()
        self.__propertiesMutex = threading.Lock()
        self.__positionX:float = 0.0
        self.__positionY:float = 0.0
        self.__selected:bool = False
        self.__mouseDeltaX:float = 0.0
        self.__mouseDeltaY:float = 0.0

        self.__modelData:vtk.vtkPolyData = modelData
        #* Place model with lower Z bound at zero
        self.__positionZ:float = self.__modelData.GetBounds()[4]

        translation = vtk.vtkTransform()
        translation.Translate(self.__positionX, self.__positionY, self.__positionZ)

        self.__modelFilterTranslate:vtk.vtkTransformPolyDataFilter = vtk.vtkTransformPolyDataFilter()
        self.__modelFilterTranslate.SetInputData(self.__modelData)
        self.__modelFilterTranslate.SetTransform(translation)
        self.__modelFilterTranslate.Update()

        #* Model Mapper
        self.__modelMapper:vtk.vtkPolyDataMapper = vtk.vtkPolyDataMapper()
        self.__modelMapper.SetInputConnection(self.__modelFilterTranslate.GetOutputPort())
        self.__modelMapper.ScalarVisibilityOff()

        #* Model Actor
        self.__modelActor:vtk.vtkActor = vtk.vtkActor()
        self.__modelActor.SetMapper(self.__modelMapper)
        self.__modelActor.GetProperty().SetInterpolationToFlat()

        self.__modelActor.GetProperty().SetAmbient(0.1)
        self.__modelActor.GetProperty().SetDiffuse(0.7)
        self.__modelActor.GetProperty().SetSpecular(0.3)
        self.__setColor(m_defaultModelColor)

        self.__modelActor.SetPosition(0.0, 0.0, 0.0)

    def getModelActor(self) -> vtk.vtkActor:
        return self.__modelActor


    def getPositionX(self) -> float:
        self.__propertiesMutex.acquire()
        positionX = self.__positionX
        self.__propertiesMutex.release()
        return positionX

    def getPositionY(self) -> float:
        self.__propertiesMutex.acquire()
        positionY = self.__positionY
        self.__propertiesMutex.release()
        return positionY

    def __setPositionX(self, positionX:float):
        if self.__positionX != positionX:
            self.__positionX = positionX
            self.positionXChanged.emit(self.__positionX)

    def __setPositionY(self, positionY:float):
        if self.__positionY != positionY:
            self.__positionY = positionY
            self.positionYChanged.emit(self.__positionY)


    def translateToPosition(self, x:float,  y:float):
        if self.__positionX == x and self.__positionY == y:
            return

        self.__propertiesMutex.acquire()
        self.__setPositionX(x)
        self.__setPositionY(y)
        self.__propertiesMutex.release()

        translation = vtk.vtkTransform()
        translation.Translate(self.__positionX, self.__positionY, self.__positionZ)
        self.__modelFilterTranslate.SetTransform(translation)
        self.__modelFilterTranslate.Update()

        self.positionXChanged.emit(self.__positionX)
        self.positionYChanged.emit(self.__positionY)


    def setSelected(self, selected:bool):
        if self.__selected != selected:
            self.__selected = selected

            self.updateModelColor()

    def updateModelColor(self):
        if self.__selected:
            self.__setColor(m_selectedModelColor)
        else:
            self.__setColor(m_defaultModelColor)

    def __setColor(self, color:QColor):
        self.__modelActor.GetProperty().SetColor(color.redF(), color.greenF(), color.blueF())


    def getMouseDeltaX(self) -> float:
        return self.__mouseDeltaX

    def getMouseDeltaY(self) -> float:
        return self.__mouseDeltaY

    def setMouseDeltaXY(self, deltaX:float, deltaY:float):
        self.__mouseDeltaX = deltaX
        self.__mouseDeltaY = deltaY
