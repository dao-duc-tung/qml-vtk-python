import os, fnmatch, sys

from PySide2.QtCore import (
    QSize,
    qDebug,
    Qt,
    QEvent,
    QObject,
    Slot,
    QPointF,
    QPoint,
    Signal,
)
from PySide2.QtGui import (
    QOpenGLFramebufferObject,
    QOpenGLFramebufferObjectFormat,
    QOpenGLFunctions,
    QMouseEvent,
    QHoverEvent,
    QWheelEvent,
    QKeyEvent,
    QCursor,
)

if sys.platform == "win32":
    try:
        PY_EXE_PATH = os.path.dirname(sys.executable)
        PYSIDE2_RCC = os.path.join(PY_EXE_PATH, "Scripts", "pyside2-rcc.exe")
        assert os.path.exists(PYSIDE2_RCC)
    except AssertionError:
        print("PySide2 is not found! PySide2 may be installed on Anaconda!")
        try:
            import PySide2

            PYSIDE2_PKG_PATH = os.path.abspath(
                os.path.join(PySide2.__file__, os.pardir)
            )
            PYSIDE2_RCC = os.path.join(PYSIDE2_PKG_PATH, "pyside2-rcc.exe")
        except ImportError:
            print("PySide2 is not installed! Please install PySide2 first.")
elif sys.platform == "linux":
    try:
        PY_EXE_PATH = os.path.dirname(sys.executable)
        PYSIDE2_RCC = os.path.join(PY_EXE_PATH, "pyside2-rcc")
        assert os.path.exists(PYSIDE2_RCC)
    except AssertionError:
        print("pyside2-rcc is not found!")
else:
    raise NotImplementedError


def compile_resource_files(rc_dir, out_dir):
    for root, dirs, files in os.walk(rc_dir):
        for basename in files:
            pattern = "*.qrc"
            if fnmatch.fnmatch(basename, pattern):
                name_str, ext = os.path.splitext(basename)
                rc_file_path = os.path.join(root, basename)
                if out_dir:
                    py_file_path = os.path.join(out_dir, "rc_" + name_str + ".py")
                else:
                    py_file_path = os.path.join(root, "rc_" + name_str + ".py")
                cmd_string = "{0} {1} -o {2}".format(
                    PYSIDE2_RCC, rc_file_path, py_file_path
                )
                os.system(cmd_string)


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


def convertToMouseEvent(
    eventType: QEvent.Type,
    localPos: QPointF,
    button: Qt.MouseButton,
    buttons: Qt.MouseButtons,
    modifiers: Qt.KeyboardModifiers,
):
    return QMouseEvent(eventType, localPos, button, buttons, modifiers)


def get_qml_object(qml_engine, object_name, parent_object=None):
    reference_buffer = []
    if parent_object is None:
        for root_object in qml_engine.rootObjects():
            if root_object.property("objectName") == object_name:
                return root_object
            obj = root_object.findChild(QObject, object_name)
            if obj is not None:
                reference_buffer.append(obj)
                return obj
    else:
        obj = parent_object.findChild(QObject, object_name)
        if obj is not None:
            reference_buffer.append(obj)
            return obj
    return None
