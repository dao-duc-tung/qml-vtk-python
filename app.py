from CanvasHandler import CanvasHandler
import os, sys
import logging
logging.basicConfig(filename='log.ini', level=logging.DEBUG)

def set_vtk_log():
    import vtk
    log_path = os.path.join("log.ini")
    fow = vtk.vtkFileOutputWindow()
    fow.SetFileName(log_path)
    ow = vtk.vtkOutputWindow()
    ow.SetInstance(fow)

def main():
    CanvasHandler(sys.argv)

if __name__ == '__main__':
    set_vtk_log()

    from src.utils import except_hook
    sys.excepthook = except_hook

    main()
