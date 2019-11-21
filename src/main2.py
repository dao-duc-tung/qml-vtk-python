from PySide2.QtCore import QUrl, qDebug, QObject
from PySide2.QtGui import QGuiApplication, QOpenGLFramebufferObjectFormat, QOpenGLFramebufferObject
from PySide2.QtQml import qmlRegisterType, QQmlApplicationEngine
from PySide2.QtQuick import QQuickItem, QQuickView, QQuickFramebufferObject
from PySide2.QtWidgets import QApplication


class FbItemRenderer(QQuickFramebufferObject.Renderer):
    def __init__(self, parent=None):
        super(FbItemRenderer, self).__init__()
        qDebug("Creating FbItemRenderer")

    def createFrameBufferObject(self, size):
        qDebug("Creating FrameBufferObject")
        format = QOpenGLFramebufferObjectFormat()
        format.setAttachment(QOpenGLFramebufferObject.Depth)
        return QOpenGLFramebufferObject(size, format)

    def synchronize(self, item):
        qDebug("Synchronizing")

    def render(self):
        qDebug("Render")
        # Called with the FBO bound and the viewport set.
        # ... Issue OpenGL commands.


class FBORenderItem(QQuickFramebufferObject):
    def __init__(self, parent=None):
        qDebug("Create fborenderitem")
        super(FBORenderItem, self).__init__(parent)

    def createRenderer(self):
        qDebug("Create renderer")
        return FbItemRenderer()


if __name__ == '__main__':
    import sys

    # app = QGuiApplication(sys.argv)
    app = QApplication(sys.argv)

    # qmlRegisterType(FBORenderItem, "Renderer", 1, 0, "FBORenderer")

    # view = QQuickView()
    # view.setSource(QUrl("resources/main2.qml"))
    # view.show()

    engine = QQmlApplicationEngine()
    print(engine.importPathList())

    engine.load(QUrl.fromLocalFile('resources\\main2.qml'))

    # rootObject = engine.rootObjects()[0] # returns QObject
    # fboItem = rootObject.findChild(FBORenderItem, 'fboRenderItem')

    sys.exit(app.exec_())
