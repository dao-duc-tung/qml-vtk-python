import logging
import os
import sys

from PySide2.QtCore import Qt, QTimer, Signal
from PySide2.QtGui import QSurfaceFormat
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide2.QtWidgets import QApplication
import vtk

from src.pieces.graphics import Fbo
from src.ctrls import MainCtrl
from src.utils import *

logging.basicConfig(filename="log.ini", level=logging.DEBUG)


def set_vtk_log():
    log_path = os.path.join("log.ini")
    fow = vtk.vtkFileOutputWindow()
    fow.SetFileName(log_path)
    ow = vtk.vtkOutputWindow()
    ow.SetInstance(fow)


def register_custom_qml_object():
    qmlRegisterType(Fbo, "QmlVtk", 1, 0, "Fbo")


def compile_qml():
    from src.utils import compile_resource_files

    compile_resource_files(rc_dir="src/views", out_dir="src/views")
    if os.path.isfile(os.path.join("src/views/rc_qml.py")):
        from src.views.rc_qml import qInitResources

        qInitResources()


class App(QApplication):
    sig_postprocess = Signal()

    def __init__(self, sys_argv):
        sys_argv += ["-style", "material"]  #! MUST HAVE
        super(App, self).__init__(sys_argv)
        self.engine = QQmlApplicationEngine()
        self.__mainCtrl = MainCtrl(self.engine)

    def postprocess_signal_binding(self):
        def postprocess():
            mainView = get_qml_object(self.engine, "MainView")
            if mainView.property("active"):
                self.__mainCtrl.setup()
            else:
                self.sig_postprocess.emit()

        self.sig_postprocess.connect(postprocess, Qt.QueuedConnection)
        self.sig_postprocess.emit()


def main():
    register_custom_qml_object()
    compile_qml()

    app = App(sys.argv)

    if len(app.engine.rootObjects()) == 0:
        print("No QML file is loaded!")
        return

    QTimer.singleShot(0, app.postprocess_signal_binding)
    sys.exit(app.exec_())


if __name__ == "__main__":
    set_vtk_log()

    sys.excepthook = except_hook

    main()
