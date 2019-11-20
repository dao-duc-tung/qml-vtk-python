from CanvasHandler import CanvasHandler
import os, sys

def set_vtk_log():
    import vtk
    log_path = os.path.join("vtk_log.txt")
    fow = vtk.vtkFileOutputWindow()
    fow.SetFileName(log_path)
    ow = vtk.vtkOutputWindow()
    ow.SetInstance(fow)

# class QtVtkPy(QApplication):
#     def __init__(self, sys_argv):
#         super().__init__(sys_argv)
#         sys_argv += ['--style', 'material']
#         self.__app = CanvasHandler(sys.argv)

def main():
    CanvasHandler(sys.argv)
    # app = QApplication(sys.argv)
    # sys.exit(app.exec_())

if __name__ == '__main__':
    set_vtk_log()

    from debug import except_hook
    sys.excepthook = except_hook

    if sys.platform == "win32":
        from multiprocessing import freeze_support

        freeze_support()
    main()
