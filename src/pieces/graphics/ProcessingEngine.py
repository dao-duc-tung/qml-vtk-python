from PySide2.QtCore import QObject, QUrl, qDebug, qCritical, QFileInfo

from Model import Model
import vtk

class ProcessingEngine():
    def __init__(self):
        self.__models = [] # List of Model

    def addModel(self, modelFilePath:QUrl) -> Model:
        qDebug('ProcessingEngine::addModel()')
        modelFilePathExtension = QFileInfo(modelFilePath).suffix().lower() # returns QString

        objReader = vtk.vtkOBJReader()
        stlReader = vtk.vtkSTLReader()
        inputData = None # vtkPolyData

        if modelFilePathExtension == 'obj':
            #* Read OBJ file
            objReader.SetFileName(modelFilePath)
            objReader.Update()
            inputData = objReader.GetOutput()
        else:
            #* Read STL file
            stlReader.SetFileName(modelFilePath)
            stlReader.Update()
            inputData = stlReader.GetOutput()

        #* Preprocess the polydata
        preprocessedPolydata = self.preprocessPolydata(inputData) # vtkPolyData

        #* Create Model instance and insert it into the vector
        model = Model(preprocessedPolydata)
        self.__models.append(model)

        return self.__models[-1]

    def preprocessPolydata(self, inputData:vtk.vtkPolyData) -> vtk.vtkPolyData:
        #* Center the polygon
        center = [0.0, 0.0, 0.0]
        inputData.GetCenter(center)

        translation = vtk.vtkTransform()
        translation.Translate(-center[0], -center[1], -center[2])

        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetInputData(inputData)
        transformFilter.SetTransform(translation)
        transformFilter.Update()

        #* Normals - For the Gouraud interpolation to work
        normals = vtk.vtkPolyDataNormals()
        normals.SetInputData(transformFilter.GetOutput())
        normals.ComputePointNormalsOn()
        normals.Update()

        return normals.GetOutput()

    def placeModel(self, model:Model):
        qDebug('ProcessingEngine::placeModel()')
        model.translateToPosition(0, 0)

    def setModelsRepresentation(self, modelsRepresentationOption:int):
        for model in self.__models:
            model.getModelActor().GetProperty().SetRepresentation(modelsRepresentationOption)

    def setModelsOpacity(self, modelsOpacity:float):
        for model in self.__models:
            model.getModelActor().GetProperty().SetOpacity(modelsOpacity)

    def setModelsGouraudInterpolation(self, enableGouraudInterpolation:bool):
        for model in self.__models:
            if enableGouraudInterpolation:
                model.getModelActor().GetProperty().SetInterpolationToGouraud()
            else:
                model.getModelActor().GetProperty().SetInterpolationToFlat()

    def updateModelsColor(self):
        for model in self.__models:
            model.updateModelColor()

    def getModelFromActor(self, modelActor:vtk.vtkActor) -> Model:
        for model in self.__models:
            if model.getModelActor() == modelActor:
                return model
        qDebug('Cannot get model from actor')
        return None
