# from PySide2.QtCore import QUrl, qDebug, QObject, Signal, Property, Slot
# from PySide2.QtGui import QGuiApplication, QOpenGLFramebufferObjectFormat, QOpenGLFramebufferObject
# from PySide2.QtQml import qmlRegisterType, QQmlApplicationEngine
# from PySide2.QtQuick import QQuickItem, QQuickView, QQuickFramebufferObject
# from PySide2.QtWidgets import QApplication


from PySide2 import QtCore, QtGui, QtQuick, QtQml
import squircle
import os, sys

if __name__ == '__main__':
    app = QtGui.QGuiApplication( sys.argv )

    QtQml.qmlRegisterType( squircle.Squircle, "OpenGLUnderQML", 1, 0, "Squircle" )

    view = QtQuick.QQuickView()
    view.setResizeMode( QtQuick.QQuickView.SizeRootObjectToView )
    view.setSource( QtCore.QUrl( "resources//main2.qml" ) )
    view.show()

    sys.exit( app.exec_() )
