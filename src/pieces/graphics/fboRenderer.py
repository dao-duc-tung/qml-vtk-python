from queue import Queue
from threading import Lock
from typing import List, Optional

from PySide2.QtCore import (
    QEvent,
    QObject,
    QSize,
    Qt,
)
from PySide2.QtGui import (
    QCursor,
    QMouseEvent,
    QOpenGLFramebufferObject,
    QOpenGLFramebufferObjectFormat,
    QOpenGLFunctions,
)
from PySide2.QtQuick import QQuickFramebufferObject
from PySide2.QtWidgets import QApplication

import vtk
from src.pieces import graphics
from src.utils import *


class FboRenderer(QQuickFramebufferObject.Renderer, QObject):
    def __init__(self):
        super(FboRenderer, self).__init__()

        self.__glFunc = QOpenGLFunctions()
        self.rw = vtk.vtkExternalOpenGLRenderWindow()
        self.rwi = vtk.vtkGenericRenderWindowInteractor()
        self.rwi.SetRenderWindow(self.rw)
        self.rw.OpenGLInitContext()
        self.__isOpenGLStateInitialized = False

        self.__openGLFbo: QOpenGLFramebufferObject = None
        self.__fbo: graphics.Fbo = None

        self.__lastMouseButtonEvent: QMouseEvent = None
        self.__lastMouseMoveEvent: QMouseEvent = None

        self.commandQueue = Queue()
        self.commandQueueLock = Lock()

    def createFramebufferObject(self, size: QSize) -> QOpenGLFramebufferObject:
        gl_format = QOpenGLFramebufferObjectFormat()
        gl_format.setAttachment(QOpenGLFramebufferObject.CombinedDepthStencil)
        self.__openGLFbo = QOpenGLFramebufferObject(size, gl_format)
        return self.__openGLFbo

    def synchronize(self, item: graphics.Fbo):
        if not self.__fbo:
            self.__fbo = item

        (w, h) = self.rw.GetSize()
        if int(self.__fbo.width()) != w or int(self.__fbo.height()) != h:
            self.rw.SetSize(int(self.__fbo.width()), int(self.__fbo.height()))

        if (
            self.__fbo.lastMouseButtonEvent
            and not self.__fbo.lastMouseButtonEvent.isAccepted()
        ):
            self.__lastMouseButtonEvent = cloneMouseEvent(
                self.__fbo.lastMouseButtonEvent
            )
            self.__lastMouseButtonEvent.ignore()
            self.__fbo.lastMouseButtonEvent.accept()
        if (
            self.__fbo.lastMouseMoveEvent
            and not self.__fbo.lastMouseMoveEvent.isAccepted()
        ):
            self.__lastMouseMoveEvent = cloneMouseEvent(self.__fbo.lastMouseMoveEvent)
            self.__lastMouseMoveEvent.ignore()
            self.__fbo.lastMouseMoveEvent.accept()

    def render(self):
        if not self.__isOpenGLStateInitialized:
            self.__openGLInitState()
            self.__isOpenGLStateInitialized = True

        if self.__lastMouseButtonEvent and not self.__lastMouseButtonEvent.isAccepted():
            self.__processMouseButtonEvent(self.__lastMouseButtonEvent)
            self.__lastMouseButtonEvent.accept()
        if self.__lastMouseMoveEvent and not self.__lastMouseMoveEvent.isAccepted():
            self.__processMouseMoveEvent(self.__lastMouseMoveEvent)
            self.__lastMouseMoveEvent.accept()

        with self.commandQueueLock:
            while not self.commandQueue.empty():
                cmd = self.commandQueue.get()
                cmd.execute()

        self.__fbo.window().resetOpenGLState()

    def __openGLInitState(self):
        self.rw.OpenGLInitState()
        self.rw.MakeCurrent()
        self.__glFunc.initializeOpenGLFunctions()
        self.__glFunc.glUseProgram(0)

    def __setEventInformation(self, x, y, ctrl, shift, key, repeat=0, keysum=None):
        scale = self.__getPixelRatio()
        if self.__fbo.mirrorVertically():
            (w, h) = self.rw.GetSize()
            y = h - y

        self.rwi.SetEventInformation(
            int(round(x * scale)),
            int(round(y * scale)),
            ctrl,
            shift,
            key,
            repeat,
            keysum,
        )

    def __processMouseButtonEvent(self, event: QMouseEvent):
        ctrl, shift = self.__getCtrlShift(event)
        if event.type() == QEvent.MouseButtonPress:
            repeat = 0
            self.__setEventInformation(
                event.x(), event.y(), ctrl, shift, chr(0), repeat, None
            )
            if event.button() == Qt.LeftButton:
                self.rwi.LeftButtonPressEvent()
            elif event.button() == Qt.RightButton:
                self.rwi.RightButtonPressEvent()
        elif event.type() == QEvent.MouseButtonRelease:
            repeat = 0
            self.__setEventInformation(
                event.x(), event.y(), ctrl, shift, chr(0), repeat, None
            )
            if event.button() == Qt.LeftButton:
                self.rwi.LeftButtonReleaseEvent()
            elif event.button() == Qt.RightButton:
                self.rwi.RightButtonReleaseEvent()

    def __processMouseMoveEvent(self, event: QMouseEvent):
        ctrl, shift = self.__getCtrlShift(event)
        self.__setEventInformation(event.x(), event.y(), ctrl, shift, chr(0), 0, None)
        self.rwi.MouseMoveEvent()

    def __getCtrlShift(self, event):
        ctrl = shift = False

        if hasattr(event, "modifiers"):
            if event.modifiers() & Qt.ShiftModifier:
                shift = True
            if event.modifiers() & Qt.ControlModifier:
                ctrl = True
        else:
            if self.__saveModifiers & Qt.ShiftModifier:
                shift = True
            if self.__saveModifiers & Qt.ControlModifier:
                ctrl = True

        return ctrl, shift

    def __getPixelRatio(self):
        # Source: https://stackoverflow.com/a/40053864/3388962
        pos = QCursor.pos()
        for screen in QApplication.screens():
            rect = screen.geometry()
            if rect.contains(pos):
                return screen.devicePixelRatio()
        # Should never happen, but try to find a good fallback.
        return QApplication.devicePixelRatio()
