from src.graphics.vtkModels import VtkModel

import vtk


class RendererModel(VtkModel):
    @property
    def model(self):
        return self.__renderer

    def __init__(self, name: str):
        super().__init__(name)
        self.__renderer = vtk.vtkRenderer()

    def config(self):
        self.__renderer.SetBackground(0, 0, 0)
        self.__renderer.GradientBackgroundOn()
        self.__renderer.ResetCameraClippingRange()
        self.__renderer.ResetCamera()

    def focusCamera(self):
        camera = self.__renderer.GetActiveCamera()
        camera.SetFocalPoint(0, 0, 0)
        camera.SetViewUp(0, 0, 1)
        camera.SetPosition(0, -1, 0)
        self.__renderer.ResetCameraClippingRange()
        self.__renderer.ResetCamera()

    def addActor(self, actor: vtk.vtkActor):
        self.__renderer.AddActor(actor)

    def removeActor(self, actor: vtk.vtkActor):
        self.__renderer.RemoveActor(actor)

    def setBackgroundColor(self, color: tuple):
        self.__renderer.SetBackground(color)
