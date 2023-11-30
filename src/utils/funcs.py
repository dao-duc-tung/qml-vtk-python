import fnmatch
import os
import sys

from PySide6.QtCore import QEvent, QObject, QPointF, Qt
from PySide6.QtGui import QMouseEvent, QWheelEvent, QSurfaceFormat


if sys.platform == "win32":
    try:
        PY_EXE_PATH = os.path.dirname(sys.executable)
        PYSIDE6_RCC = os.path.join(PY_EXE_PATH, "pyside6-rcc.exe")
        assert os.path.exists(PYSIDE6_RCC)
    except AssertionError:
        print("PySide6 is not found! PySide6 may be installed on Anaconda!")
        try:
            import PySide6

            PYSIDE2_PKG_PATH = os.path.abspath(
                os.path.join(PySide6.__file__, os.pardir)
            )
            PYSIDE6_RCC = os.path.join(PYSIDE2_PKG_PATH, "pyside6-rcc.exe")
        except ImportError:
            print("PySide6 is not installed! Please install PySide6 first.")
elif sys.platform == "linux":
    try:
        PY_EXE_PATH = os.path.dirname(sys.executable)
        PYSIDE6_RCC = os.path.join(PY_EXE_PATH, "pyside6-rcc")
        assert os.path.exists(PYSIDE6_RCC)
    except AssertionError:
        print("pyside6-rcc is not found!")
else:
    raise NotImplementedError


def compileResourceFiles(rcDir, outDir):
    for root, dirs, files in os.walk(rcDir):
        for basename in files:
            pattern = "*.qrc"
            if fnmatch.fnmatch(basename, pattern):
                nameStr, ext = os.path.splitext(basename)
                rcFilePath = os.path.join(root, basename)
                if outDir:
                    pyFilePath = os.path.join(outDir, "rc_" + nameStr + ".py")
                else:
                    pyFilePath = os.path.join(root, "rc_" + nameStr + ".py")
                cmdStr = "{0} {1} -o {2}".format(PYSIDE6_RCC, rcFilePath, pyFilePath)
                os.system(cmdStr)

def cloneMouseEvent(event: QMouseEvent):
    return QMouseEvent(
        event.type(),
        event.localPos(),
        event.windowPos(),
        event.screenPos(),
        event.button(),
        event.buttons(),
        event.modifiers(),
        event.source(),
    )


def cloneWheelEvent(event: QWheelEvent):
    return QWheelEvent(
        event.position(),
        event.globalPosition(),
        event.pixelDelta(),
        event.angleDelta(),
        event.buttons(),
        event.modifiers(),
        event.phase(),
        event.inverted(),
        event.source(),
    )


def convertToMouseEvent(
    eventType: QEvent.Type,
    localPos: QPointF,
    button: Qt.MouseButton,
    buttons: Qt.MouseButtons,
    modifiers: Qt.KeyboardModifiers,
):
    return QMouseEvent(eventType, localPos, button, buttons, modifiers)


def getQmlObject(qmlEngine, objectName, parentObj=None):
    referenceBuffer = []
    if parentObj is None:
        for root_object in qmlEngine.rootObjects():
            if root_object.property("objectName") == objectName:
                return root_object
            obj = root_object.findChild(QObject, objectName)
            if obj is not None:
                referenceBuffer.append(obj)
                return obj
    else:
        obj = parentObj.findChild(QObject, objectName)
        if obj is not None:
            referenceBuffer.append(obj)
            return obj
    return None


def setDefaultSurfaceFormat(stereoCapable):
    """ Ported from: https://github.com/Kitware/VTK/blob/master/GUISupport/Qt/QVTKRenderWindowAdapter.cxx
    """
    fmt = QSurfaceFormat()
    fmt.setRenderableType(QSurfaceFormat.OpenGL)
    fmt.setVersion(3, 2)
    fmt.setProfile(QSurfaceFormat.CoreProfile)
    fmt.setSwapBehavior(QSurfaceFormat.DoubleBuffer)
    fmt.setRedBufferSize(8)
    fmt.setGreenBufferSize(8)
    fmt.setBlueBufferSize(8)
    fmt.setDepthBufferSize(8)
    fmt.setAlphaBufferSize(8)
    fmt.setStencilBufferSize(0)
    fmt.setStereo(stereoCapable)
    fmt.setSamples(0)

    return fmt
