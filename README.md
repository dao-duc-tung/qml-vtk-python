# A Python-based project on QML-VTK combination

The source code is based on [Nicanor Romero Venier's project](https://github.com/nicanor-romero/QtVtk)

## Description

This project provides a solution to render VTK objects on QML-based UI.

Moreover, I re-organize the architecture of the code and make it simple and scalable.

The architecture can be described as below:

- `MVVM pattern` is used. `Business models` are put inside `src/models` folder. `Views` are put inside `src/views` folder. `View-models` are put inside `src/ctrls` folder.
- Data/Variables which are cached/stored while the app is running can be saved inside `Business models`.
- Every data/variables inside `Business models` are watched. The `Business models` will emit a `Signal` if data is changed.
- The `View-Models` will catch that `Signal` and process the data transferred along with the `Signal`.
- The `View-Models` also expose the functions to the `Views`. These `View-Model`'s functions should change the data in `Business models`.
- Users will call `View-Models`'s functions through UI on the `Views`.
---
- `Fbo` and `FboRenderer` classes support graphical rendering process.
- src/graphics/vtkModels folder has VTK-related models which support the creation of VTK objects.
- `ProcessingEngine` class support VTK-related models managing.
---
- Every graphical actions should be done inside Render Thread.
- `Command pattern` is used to make sure those actions will be done correctly.

## Availability

The code was tested using Python 3.6.6, PySide2 5.13.2 and VTK 8.1.1 (built with vtkRenderingExternal module in Release mode), VTK 8.1.2 (built without vtkRenderingExternal module in Debug mode), VTK 8.2.0 (built without vtkRenderingExternal module in Debug mode) in Windows 10.

The code was tested using Python 3.6.6, PySide2 5.13.2, VTK 8.1.2 (with vtkRenderingExternal), and Anaconda3 in Ubuntu 16.04.

[[Tested by szmurlor](https://github.com/szmurlor/QtVTK-Py)] The code was also tested in Ubuntu 18.04 Linux under [Miniconda](https://docs.conda.io/en/latest/miniconda.html) environment with Python 3.7.5, PySide2 5.13.1 (from conda-forge), qt 5.12.5 and VTK 8.2. When using libraries from the Miniconda distribution, the options are not required (or are simply already included).

## Installation

You should find some ways to install VTK or follow [szmurlor's instruction](https://github.com/szmurlor/QtVTK-Py)

```shell
conda create --name QmlVtk python=3.6.6
conda activate QmlVtk

conda install -c conda-forge pyside2 # Linux
pip install PySide2 # Windows
```

## Update

### 22/04/2020

The application now is simplified

Check out [this commit](https://github.com/dao-duc-tung/QtVTK-Py/commit/5d70062b1a931dabef072d4f4e58a73e9828f830) for previous version

## Troubleshoot

In [Nicanor's post](https://medium.com/bq-engineering/integrating-qtquickcontrols-2-with-vtk-df54bbb99de3), he claimed that "in order for this code to work you will need to add the vtkRenderingExternal module when compiling VTK". I'm not sure about this module but I also tested this porject with VTK 8.1.2 and VTK 8.2.0 which are built without vtkRenderingExternal module.

Anyway, thanks Nicanor very much!

## Example

![Import and view STL files](resources/QmlVtk_1.gif "Import and view STL files")

![Overlay QtQuickControls2 components](resources/QmlVtk_2.gif "Overlay QtQuickControls2 components")
