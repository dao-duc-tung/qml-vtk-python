# A python-based project on VTK-QML combination

The source code is based on [Nicanor Romero Venier's project](https://github.com/nicanor-romero/QtVtk)

## Description

The code was tested using Python 3.6.6, PySide2 5.13.2 and VTK 8.1.1 (built with vtkRenderingExternal module in Release mode), VTK 8.1.2 (built without vtkRenderingExternal module in Debug mode), VTK 8.2.0 (built without vtkRenderingExternal module in Debug mode) in Windows 10.

The code was also tested in Ubuntu 18.04 Linux under [Miniconda](https://docs.conda.io/en/latest/miniconda.html) environment with Python 3.7.5, PySide2 5.13.1 (from conda-forge), qt 5.12.5 and VTK 8.2. 

In [Nicanor's post](https://medium.com/bq-engineering/integrating-qtquickcontrols-2-with-vtk-df54bbb99de3), he claimed that "in order for this code to work you will need to add the vtkRenderingExternal module when compiling VTK". I'm not sure about this module but I also tested this porject with VTK 8.1.2 and VTK 8.2.0 which are built without vtkRenderingExternal module. When using libraries from the Miniconda distribution, the options are not required (or are simply already included).

Anyway, thanks Nicanor very much!

## Installation

Modify your qt.conf file (in python install folder) as below if needed:

```
[Paths]
Prefix = python-folder/Lib/site-packages/PySide2
```

## Miniconda setup

You can start by creating a new conda environment with the following required packages:

```sh
conda create --name vtkqml python=3.7
conda activate vtkqml
conda install -c conda-forge qt vtk pyside2 numpy pandas pyopengl
```

Then, being in the root folder of the repository run the command:

```sh
python src/main.py
```

## Example

![Import and view STL files](resources/QtVtk_1.gif "Import and view STL files")

![Overlay QtQuickControls2 components](resources/QtVtk_2.gif "Overlay QtQuickControls2 components")
