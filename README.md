# A python-based project on VTK-QML combination

The source code is based on [Nicanor Romero Venier's project](https://github.com/nicanor-romero/QtVtk)

## Description

The code was tested using Python 3.6.6, PySide2 >= 5.13.2 and VTK 8.1.1 (built with vtkRenderingExternal module in Release mode), VTK 8.1.2 (built without vtkRenderingExternal module in Debug mode), VTK 8.2.0 (built without vtkRenderingExternal module in Debug mode) in Windows 10.

In [Nicanor's post](https://medium.com/bq-engineering/integrating-qtquickcontrols-2-with-vtk-df54bbb99de3), he claimed that "in order for this code to work you will need to add the vtkRenderingExternal module when compiling VTK". I'm not sure about this module but I also tested this porject with VTK 8.1.2 and VTK 8.2.0 which are built without vtkRenderingExternal module.

Anyway, thanks Nicanor very much!

## Installation

```shell
conda create --name QmlVtk python=3.6.6
conda activate QmlVtk

conda install -c conda-forge pyside2 # Linux
pip install PySide2 # Windows
```

## Example

The application now is simplified

Check out [this commit](https://github.com/dao-duc-tung/QtVTK-Py/commit/5d70062b1a931dabef072d4f4e58a73e9828f830) for previous version

![Import and view STL files](resources/QmlVtk_1.gif "Import and view STL files")

![Overlay QtQuickControls2 components](resources/QmlVtk_2.gif "Overlay QtQuickControls2 components")
