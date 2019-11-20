from PyQt5.QtCore import QObject, QApp, QUrl, qDebug, qCritical, QFileInfo, pyqtSignal
from PyQt5.QtGui import QColor
import threading
import vtk

class Model(QObject):
    positionXChanged = pyqtSignal(float)
	positionYChanged = pyqtSignal(float)

    __m_defaultModelColor:QColor = QColor("#0277bd")
    __m_selectedModelColor:QColor = QColor("#03a9f4")

    def __init__(self, modelData:vtk.vtkPolyData):
        self.__m_propertiesMutex = threading.Lock()
        self.__m_positionX:float = 0.0
        self.__m_positionY:float = 0.0
        self.__m_selected:bool = False
        self.__m_mouseDeltaX:float = 0.0
        self.__m_mouseDeltaY:float = 0.0

        self.__m_modelData:vtk.vtkPolyData = modelData
        #* Place model with lower Z bound at zero
        self.__m_positionZ:float = self.__m_modelData.GetBounds()[4]

        translation = vtk.vtkTransform()
        translation.Translate(m_positionX, m_positionY, m_positionZ)

        self.__m_modelFilterTranslate:vtk.vtkTransformPolyDataFilter = vtk.vtkTransformPolyDataFilter()
        self.__m_modelFilterTranslate.SetInputData(m_modelData)
        self.__m_modelFilterTranslate.SetTransform(translation)
        self.__m_modelFilterTranslate.Update()

        #* Model Mapper
        self.__m_modelMapper:vtk.vtkPolyDataMapper = vtkPolyDataMapper()
        self.__m_modelMapper.SetInputConnection(self.__m_modelFilterTranslate.GetOutputPort())
        self.__m_modelMapper.ScalarVisibilityOff()

        #* Model Actor
        self.__m_modelActor:vtk.vtkActor = vtk.vtkActor()
        self.__m_modelActor.SetMapper(self.__m_modelMapper)
        self.__m_modelActor.GetProperty().SetInterpolationToFlat()

        self.__m_modelActor.GetProperty().SetAmbient(0.1)
        self.__m_modelActor.GetProperty().SetDiffuse(0.7)
        self.__m_modelActor.GetProperty().SetSpecular(0.3)
        self.__setColor(m_defaultModelColor)

        self.__m_modelActor.SetPosition(0.0, 0.0, 0.0)

    def getModelActor(self) -> vtk.vtkActor:
        return m_modelActor


    def getPositionX(self) -> float:
        self.__m_propertiesMutex.acquire()
        positionX = self.__m_positionX
        self.__m_propertiesMutex.release()
        return positionX

    def getPositionY(self) -> float:
        self.__m_propertiesMutex.acquire()
        positionY = self.__m_positionY
        self.__m_propertiesMutex.release()
        return positionY

    def __setPositionX(self, positionX:float):
        if self.__m_positionX != positionX:
            self.__m_positionX = positionX
            self.positionXChanged.emit(self.__m_positionX)

    def __setPositionY(self,const double positionY):
        if self.__m_positionY != positionY:
            self.__m_positionY = positionY
            self.positionYChanged.emit(self.__m_positionY)


    def translateToPosition(self,const double x, const double y):
        if self.__m_positionX == x and self.__m_positionY == y:
            return

        self.__m_propertiesMutex.acquire()
        self.__setPositionX(x)
        self.__setPositionY(y)
        self.__m_propertiesMutex.release()

        translation = vtk.vtkTransform()
        translation.Translate(self.__m_positionX, self.__m_positionY, self.__m_positionZ)
        self.__m_modelFilterTranslate.SetTransform(translation)
        self.__m_modelFilterTranslate.Update()

        self.positionXChanged.emit(self.__m_positionX)
        self.positionYChanged.emit(self.__m_positionY)


    def setSelected(self, selected:bool):
        if self.__m_selected != selected:
            self.__m_selected = selected

            self.updateModelColor()

    @staticmethod
    def setSelectedModelColor(self, selectedModelColor:QColor):
        self.__m_selectedModelColor = selectedModelColor

    def updateModelColor(self):
        if self.__m_selected:
            self.__setColor(self.__m_selectedModelColor)
        else
            self.__setColor(self.__m_defaultModelColor)

    def __setColor(self, color:QColor):
        self.__m_modelActor.GetProperty().SetColor(color.redF(), color.greenF(), color.blueF())


    def getMouseDeltaX(self) -> float:
        return self.__m_mouseDeltaX

    def getMouseDeltaY(self) -> float:
        return self.__m_mouseDeltaY

    def setMouseDeltaXY(self, deltaX:float, deltaY:float):
        self.__m_mouseDeltaX = deltaX
        self.__m_mouseDeltaY = deltaY
