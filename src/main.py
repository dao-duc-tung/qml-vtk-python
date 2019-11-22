# from PySide2.QtWidgets import QApplication, QLabel
# from PyQt5.QtWidgets import QApplication, QLabel
from CanvasHandler import CanvasHandler
import os, sys

def set_vtk_log():
    import vtk
    log_path = os.path.join("log.ini")
    fow = vtk.vtkFileOutputWindow()
    fow.SetFileName(log_path)
    ow = vtk.vtkOutputWindow()
    ow.SetInstance(fow)

# class QtVtkPy(QApplication):
#     def __init__(self, sys_argv):
#         # super(QtVtkPy, self).__init__(sys_argv)
#         # sys_argv += ['--style', 'material']
#         self.__app = CanvasHandler(sys_argv)
        # print('a')

def main():
    CanvasHandler(sys.argv)
    # app = QtVtkPy(sys.argv)
    # sys.exit(app.exec_())
    # app = QApplication([])
    # window = QLabel('Window from label')
    # window.show()
    # app.exec_()

if __name__ == '__main__':
    set_vtk_log()

    from debug import except_hook
    sys.excepthook = except_hook

    if sys.platform == "win32":
        from multiprocessing import freeze_support

        freeze_support()
    main()
