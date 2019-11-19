from PyQt5.QtCore import QObject, QApp, QUrl, qDebug, qCritical, QFileInfo
from PyQt5.QtQuick import QQuickFramebufferObject

# TODO: QOpenGLFunctions
class QVTKFramebufferObjectRenderer(QObject, QQuickFramebufferObject.Renderer):
    def __init__(self):
        pass
