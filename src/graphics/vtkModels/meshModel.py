import vtk
from PySide2.QtCore import QFileInfo, QUrl

from .polyDataModel import PolyDataModel


class MeshModel(PolyDataModel):
    def __init__(self, name: str, modelPath: QUrl):
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
        super().__init__(name, preprocessedPolydata)
