import os, sys
import logging

from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide2.QtWidgets import QApplication

logging.basicConfig(filename='log.ini', level=logging.DEBUG)

def set_vtk_log():
    import vtk
    log_path = os.path.join("log.ini")
    fow = vtk.vtkFileOutputWindow()
    fow.SetFileName(log_path)
    ow = vtk.vtkOutputWindow()
    ow.SetInstance(fow)

def register_custom_qml_object():
    from src.pieces.graphics import FboItem
    qmlRegisterType(FboItem, 'QmlVtk', 1, 0, 'FboItem')

def compile_qml():
    from src.utils import compile_resource_files
    compile_resource_files(
        rc_dir='src/views',
        out_dir='src/views'
    )
    if os.path.isfile(os.path.join("src/views/rc_qml.py")):
        from src.views.rc_qml import qInitResources
        qInitResources()

class App(QApplication):
    def __init__(self, sys_argv):
        sys_argv += ['-style', 'material'] #! MUST HAVE
        super(App, self).__init__(sys_argv)

        from src.ctrls import MainCtrl
        self.__mainCtrl = MainCtrl()

def main():
    register_custom_qml_object()
    compile_qml()

    app = App(sys.argv)
    sys.exit(app.exec_())

if __name__ == '__main__':
    set_vtk_log()

    from src.utils import except_hook
    sys.excepthook = except_hook

    main()
