from PySide2.QtCore import QObject, QUrl, qDebug, qCritical, QFileInfo, QThread, Signal

from src.pieces.graphics import *
from src.pieces.vtkModels import *
from src.utils import *
import vtk


class MainHelper(QObject):
    def __init__(self, engine: ProcessingEngine, fbo: Fbo):
        super().__init__()
        self.__engine = engine
        self.__fbo = fbo

        self.__visual_cylinder = False
        self.renderer_color = [0, 0, 0]
        self.model_color = [127, 127, 0]

    def render(self):
        def config(*args, **kwargs):
            self.__fbo.rwi.Render()

        cmd = Cmd(callback=config)
        self.__fbo.addCommand(cmd)

    def focusCamera(self):
        def config(*args, **kwargs):
            rendererModel: RendererModel = self.__engine.getModel(ModelName.BASE)
            renderer = rendererModel.model
            camera = renderer.GetActiveCamera()
            camera.SetFocalPoint(0, 0, 0)
            camera.SetViewUp(0, 0, 1)
            camera.SetPosition(0, -1, 0)
            renderer.ResetCameraClippingRange()
            renderer.ResetCamera()

        cmd = Cmd(callback=config)
        self.__fbo.addCommand(cmd)

    def addInteractorStyle(self):
        def config(*args, **kwargs):
            interactorStyleModel = InteractorStyleModel(ModelName.STYLE_TRACKBALL)
            self.__fbo.rwi.SetInteractorStyle(interactorStyleModel.model)
            self.__fbo.rwi.Initialize()
            self.__fbo.rwi.Start()
            self.__engine.registerModel(interactorStyleModel)

        cmd = Cmd(callback=config)
        self.__fbo.addCommand(cmd)

    def addRenderer(self):
        def config(*args, **kwargs):
            rendererModel = RendererModel(ModelName.BASE)
            renderer = rendererModel.model
            renderer.SetBackground(self.renderer_color)
            renderer.GradientBackgroundOn()
            renderer.ResetCameraClippingRange()
            renderer.ResetCamera()
            camera = renderer.GetActiveCamera()

            self.__fbo.rw.AddRenderer(rendererModel.model)
            self.__engine.registerModel(rendererModel)

        cmd = Cmd(callback=config)
        self.__fbo.addCommand(cmd)

    def addMesh(self, modelPath: QUrl):
        def config(*args, **kwargs):
            modelFilePathExtension = QFileInfo(modelPath).suffix().lower()

            objReader = vtk.vtkOBJReader()
            stlReader = vtk.vtkSTLReader()
            inputData = None

            if modelFilePathExtension == "obj":
                objReader.SetFileName(modelPath)
                objReader.Update()
                inputData = objReader.GetOutput()
            elif modelFilePathExtension == "stl":
                stlReader.SetFileName(modelPath)
                stlReader.Update()
                inputData = stlReader.GetOutput()

            center = [0.0, 0.0, 0.0]
            inputData.GetCenter(center)

            translation = vtk.vtkTransform()
            translation.Translate(-center[0], -center[1], -center[2])

            transformFilter = vtk.vtkTransformPolyDataFilter()
            transformFilter.SetInputData(inputData)
            transformFilter.SetTransform(translation)
            transformFilter.Update()

            normals = vtk.vtkPolyDataNormals()
            normals.SetInputData(transformFilter.GetOutput())
            normals.ComputePointNormalsOn()
            normals.Update()

            preprocessedPolydata = normals.GetOutput()
            meshModel = PolyDataModel(ModelName.MESH_A, preprocessedPolydata)

            rendererModel: RendererModel = self.__engine.getModel(ModelName.BASE)
            renderer = rendererModel.model
            renderer.AddActor(meshModel.actor)
            self.__engine.registerModel(meshModel)

        cmd = Cmd(callback=config)
        self.__fbo.addCommand(cmd)

    def toggle_cylinder(self):
        self.__visual_cylinder = not self.__visual_cylinder

        def config(*args, **kwargs):
            if self.__visual_cylinder:
                cylinderSource = vtk.vtkCylinderSource()
                cylinderSource.SetCenter(0.0, 0.0, 0.0)
                cylinderSource.SetRadius(5.0)
                cylinderSource.SetHeight(7.0)
                cylinderSource.SetResolution(100)
                cylinderSource.Update()
                polyData = cylinderSource.GetOutput()

                polyDataModel = PolyDataModel(ModelName.CYLINDER_A, polyData)
                rendererModel: RendererModel = self.__engine.getModel(ModelName.BASE)
                renderer = rendererModel.model
                renderer.AddActor(polyDataModel.actor)
                self.__engine.registerModel(polyDataModel)
            else:
                polyDataModel = self.__engine.getModel(ModelName.CYLINDER_A)
                rendererModel: RendererModel = self.__engine.getModel(ModelName.BASE)
                renderer = rendererModel.model
                renderer.RemoveActor(polyDataModel.actor)
                self.__engine.removeModel(ModelName.CYLINDER_A)

        cmd = Cmd(callback=config)
        self.__fbo.addCommand(cmd)

    def updateRendererColor(self):
        def config(*args, **kwargs):
            rendererModel: RendererModel = self.__engine.getModel(ModelName.BASE)
            renderer = rendererModel.model
            renderer.SetBackground(self.renderer_color)

        cmd = Cmd(callback=config)
        self.__fbo.addCommand(cmd)

    def updateModelColor(self):
        color = [i / 255 for i in self.model_color]

        def config(*args, **kwargs):
            model = self.__engine.getModel(ModelName.MESH_A)
            if model:
                actor = model.actor
                actor.GetProperty().SetColor(color)

            model = self.__engine.getModel(ModelName.CYLINDER_A)
            if model:
                actor = model.actor
                actor.GetProperty().SetColor(color)

        cmd = Cmd(callback=config)
        self.__fbo.addCommand(cmd)
