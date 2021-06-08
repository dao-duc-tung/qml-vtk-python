# A Python-based project on QML-VTK combination

The source code is based on [Nicanor Romero Venier's project](https://github.com/nicanor-romero/QtVtk)

## Description

This project provides a solution to render VTK objects on QML-based UI.

Moreover, I re-organize the architecture of the code and make it simple and scalable.

The architecture can be described as below:

- [`MVVM`](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93viewmodel) architectural is used. `Model` is put inside `src/model` folder. `View` is put inside `src/view` folder. `ViewModel` is put inside `src/ctrls` folder.
- Data/Variables which are cached/stored the app states should be saved in `Model` which is implemented [`Singleton`](https://en.wikipedia.org/wiki/Singleton_pattern) design pattern.
- The `Model` will emit a `Signal` if data is changed.
- The `ViewModel` will catch that `Signal` and pass the data along with the `Signal` as the parameter.
- The `ViewModel` also exposes the methods to the `View`.
- `ViewModel`'s methods will be called through the `View`.
---
- `Fbo` and `FboRenderer` classes support graphical rendering process.
- `src/graphics/vtkModel` folder has VTK-related model which support the creation of VTK objects.
- `ProcessingEngine` class support VTK-related model managing.
---
- Every graphical actions should be done inside Render Thread.
- `Command pattern` is used to make sure those actions will be done correctly.

## Compatibility

The code was tested by using Anaconda3 and the following combinations:
- Python 3.6.6 + PySide2 5.13.2 + VTK 8.1.1/8.1.2/8.2.0 (built from source) + Ubuntu 16.04/Windows 10
- Python 3.7.10 + PySide2 5.13.2 + VTK 8.1.2 (from [pypi](https://pypi.org/project/vtk))
- Python 3.7.5 + PySide2 5.13.1 + VTK 8.2 [Thanks szmurlor](https://github.com/szmurlor/QtVTK-Py)

## Installation

```shell
conda create --name QmlVtk python=3.7
conda activate QmlVtk

conda install -c conda-forge pyside2=5.13.2 # Linux
pip install PySide2==5.13.2 # Windows

pip install vtk==8.1.2 # check compatibility section
```

## Troubleshoot

If you want to use `vtkGPUVolumeRayCastMapper`, you have to use `vtkExternalOpenGLRenderWindow` instead of `vtkGenericOpenGLRenderWindow` (in `FboRenderer` class). `vtkExternalOpenGLRenderWindow` will require VTK to be built with `vtkRenderingExternal` option. It means you have to rebuild VTK from source.

## Example

![Import and view STL files](resources/QmlVtk_1.gif "Import and view STL files")

![Overlay QtQuickControls2 components](resources/QmlVtk_2.gif "Overlay QtQuickControls2 components")
