from PyQt5.QtCore import QObject, QApp, QUrl, qDebug, qCritical, QFileInfo
from .Model import Model

class ProcessingEngine():
    def __init__(self):
        self.__m_models = [] # List of Model

    def addModel(modelFilePath:QUrl) . Model:
        qDebug('ProcessingEngine::addModelData()')
        modelFilePathExtension = QFileInfo(modelFilePath.toString()).suffix().toLower() # returns QString

        objReader = vtk.vtkOBJReader()
        stlReader = vtk.vtkSTLReader()
        inputData = None # vtkPolyData

        if modelFilePathExtension == 'obj':
            #* Read OBJ file
            objReader.SetFileName(modelFilePath.toString().toStdString().c_str())
            objReader.Update()
            inputData = objReader.GetOutput()
        else:
            #* Read STL file
            stlReader.SetFileName(modelFilePath.toString().toStdString().c_str())
            stlReader.Update()
            inputData = stlReader.GetOutput()

        #* Preprocess the polydata
        preprocessedPolydata = preprocessPolydata(inputData) # vtkPolyData

        #* Create Model instance and insert it into the vector
        model = preprocessedPolydata
        self.__m_models.append(model)

        return self.__m_models[-1]

    def preprocessPolydata(self, inputData:vtk.vtkPolyData) -> vtk.vtkPolyData:
        #* Center the polygon
        center = [0.0, 0.0, 0.0]
        inputData.GetCenter(center)

        translation = vtkTransform()
        translation.Translate(-center[0], -center[1], -center[2])

        transformFilter = vtkTransformPolyDataFilter()
        transformFilter.SetInputData(inputData)
        transformFilter.SetTransform(translation)
        transformFilter.Update()

        #* Normals - For the Gouraud interpolation to work
        normals = vtkPolyDataNormals()
        normals.SetInputData(transformFilter.GetOutput())
        normals.ComputePointNormalsOn()
        normals.Update()

        return normals.GetOutput()

    def placeModel(self, model:Model):
        qDebug('ProcessingEngine::placeModel()')
        model.translateToPosition(0, 0)

    def setModelsRepresentation(self, modelsRepresentationOption:int):
        for model in self.__m_models:
            model.getModelActor().GetProperty().SetRepresentation(modelsRepresentationOption)

    def setModelsOpacity(self, modelsOpacity:float):
        for model in self.__m_models:
            model.getModelActor().GetProperty().SetOpacity(modelsOpacity)

    def setModelsGouraudInterpolation(self, enableGouraudInterpolation:bool):
        for model in self.__m_models:
            if enableGouraudInterpolation:
                model.getModelActor().GetProperty().SetInterpolationToGouraud()
            else:
                model.getModelActor().GetProperty().SetInterpolationToFlat()

    def updateModelsColor(self):
        for model in self.__m_models:
            model.updateModelColor()

    def getModelFromActor(self, modelActor:vtk.vtkActor) -> Model:
        for model in self.__m_models:
            if model.getModelActor() == modelActor
                return model
        # TODO: Raise exception instead
        return None
