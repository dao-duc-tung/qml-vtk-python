from .polyDataModel import PolyDataModel
import vtk

class CylinderModel(PolyDataModel):
    def __init__(self, name: str):
        cylinderSource = vtk.vtkCylinderSource()
        cylinderSource.SetCenter(0.0, 0.0, 0.0)
        cylinderSource.SetRadius(5.0)
        cylinderSource.SetHeight(7.0)
        cylinderSource.SetResolution(100)
        cylinderSource.Update()
        polyData = cylinderSource.GetOutput()
        super().__init__(name, polyData)
