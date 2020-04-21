# A python-based project on VTK-QML combination

The source code is based on [Nicanor Romero Venier's project](https://github.com/nicanor-romero/QmlVtk)

## Description

The code was tested using Python 3.6.6, PySide2 5.13.2 and VTK 8.1.1 (built with vtkRenderingExternal module in Release mode), VTK 8.1.2 (built without vtkRenderingExternal module in Debug mode), VTK 8.2.0 (built without vtkRenderingExternal module in Debug mode) in Windows 10.

In [Nicanor's post](https://medium.com/bq-engineering/integrating-qtquickcontrols-2-with-vtk-df54bbb99de3), he claimed that "in order for this code to work you will need to add the vtkRenderingExternal module when compiling VTK". I'm not sure about this module but I also tested this porject with VTK 8.1.2 and VTK 8.2.0 which are built without vtkRenderingExternal module.

Anyway, thanks Nicanor very much!

## Installation

Modify your qt.conf file (in python install folder) as below if needed:

```
[Paths]
Prefix = python-folder/Lib/site-packages/PySide2
```

## Example

![Import and view STL files](resources/QmlVtk_1.gif "Import and view STL files")

![Overlay QtQuickControls2 components](resources/QmlVtk_2.gif "Overlay QtQuickControls2 components")
