import os, sys
import logging

from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType

logging.basicConfig(filename='log.ini', level=logging.DEBUG)

def set_vtk_log():
    import vtk
    log_path = os.path.join("log.ini")
    fow = vtk.vtkFileOutputWindow()
    fow.SetFileName(log_path)
    ow = vtk.vtkOutputWindow()
    ow.SetInstance(fow)

def register_custom_qml_object():
    qmlRegisterType(FboItem, 'QtVTK', 1, 0, 'VtkFboItem')

def main():
    from CanvasHandler import CanvasHandler
    CanvasHandler(sys.argv)

if __name__ == '__main__':
    set_vtk_log()
    register_custom_qml_object()

    from src.utils import except_hook
    sys.excepthook = except_hook

    main()
