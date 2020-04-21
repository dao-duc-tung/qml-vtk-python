from src.pieces.vtkModels import VtkModel

import vtk


class RendererModel(VtkModel):
    @property
    def model(self):
        return self.__model

    def __init__(self, name: str):
        super().__init__(name)
        self.__model = vtk.vtkRenderer()
