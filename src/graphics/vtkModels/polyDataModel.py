from src.graphics.vtkModels import VtkModel
import vtk


class PolyDataModel(VtkModel):
    @property
    def model(self):
        return self.__model

    @property
    def mapper(self):
        return self.__mapper

    @property
    def actor(self):
        return self.__actor

    def __init__(self, name: str, polyData):
        super().__init__(name)
        self.__model = polyData
        self.__mapper = vtk.vtkPolyDataMapper()
        self.__mapper.SetInputData(polyData)

        self.__actor = vtk.vtkActor()
        self.__actor.SetMapper(self.__mapper)
