from queue import Queue
from threading import Lock
from typing import List, Optional

from PySide6.QtCore import QEvent, QObject, QSize, Qt
from PySide6.QtGui import (
    QCursor,
    QMouseEvent,
    QOpenGLFunctions,
    QWheelEvent, QOpenGLContext,
)
from PySide6.QtOpenGL import QOpenGLFramebufferObject, QOpenGLFramebufferObjectFormat
from PySide6.QtQuick import QQuickFramebufferObject
from PySide6.QtWidgets import QApplication

import vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from src.graphics import engines
from src.utils import *


class FboRenderer(QQuickFramebufferObject.Renderer, QObject):
    def __init__(self):
        super(FboRenderer, self).__init__()
        self.commandQueue = Queue()
        self.commandQueueLock = Lock()

        # self.rw = vtk.vtkQQuickVTKRenderWindow()

        # self.rw = vtk.vtkGenericOpenGLRenderWindow()
        # The purpose of using vtkExternalOpenGLRenderWindow is
        # to use vtkGPUVolumeRayCastMapper with vtkVolume
        self.rw = vtk.vtkExternalOpenGLRenderWindow()
        self.rwi = vtk.vtkGenericRenderWindowInteractor()
        # self.rwi = QVTKRenderWindowInteractor()
        self.rwi.SetRenderWindow(self.rw)
        self.rw.OpenGLInitContext()

        self.__glFunc = QOpenGLFunctions()
        self.__isOpenGLStateInitialized = False

        self.__openGLFbo: QOpenGLFramebufferObject = None
        self.__fbo: engines.Fbo = None

        self.__lastMouseButtonEvent: QMouseEvent = None
        self.__lastMouseMoveEvent: QMouseEvent = None
        self.__lastWheelEvent: QWheelEvent = None

    def createFramebufferObject(self, size: QSize) -> QOpenGLFramebufferObject:
        glFormat = QOpenGLFramebufferObjectFormat()
        glFormat.setAttachment(QOpenGLFramebufferObject.CombinedDepthStencil)
        self.__openGLFbo = QOpenGLFramebufferObject(size, glFormat)
        return self.__openGLFbo

    def synchronize(self, item: engines.Fbo):
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
        if self.__fbo.lastWheelEvent and not self.__fbo.lastWheelEvent.isAccepted():
            self.__lastWheelEvent = cloneWheelEvent(self.__fbo.lastWheelEvent)
            self.__lastWheelEvent.ignore()
            self.__fbo.lastWheelEvent.accept()

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
        if self.__lastWheelEvent and not self.__lastWheelEvent.isAccepted():
            self.__processWheelEvent(self.__lastWheelEvent)
            self.__lastWheelEvent.accept()

        with self.commandQueueLock:
            while not self.commandQueue.empty():
                cmd = self.commandQueue.get()
                cmd.execute()

        # self.__fbo.window().resetOpenGLState()

    def __openGLInitState(self):
        self.rw.OpenGLInitState()
        self.rw.MakeCurrent()
        self.__glFunc.initializeOpenGLFunctions()
        self.__glFunc.glUseProgram(0)

    def __processMouseButtonEvent(self, event: QMouseEvent):
        ctrl, shift = self.__getCtrlShift(event)
        repeat = 0
        if event.type() == QEvent.MouseButtonDblClick:
            repeat = 1

        self.__setEventInformation(event.position(), ctrl, shift, chr(0), repeat, None)
        if (
            event.type() == QEvent.MouseButtonPress
            or event.type() == QEvent.MouseButtonDblClick
        ):
            if event.button() == Qt.LeftButton:
                self.rwi.LeftButtonPressEvent()
            elif event.button() == Qt.RightButton:
                self.rwi.RightButtonPressEvent()
            elif event.button() == Qt.MidButton:
                self.rwi.MiddleButtonPressEvent()
        elif event.type() == QEvent.MouseButtonRelease:
            if event.button() == Qt.LeftButton:
                self.rwi.LeftButtonReleaseEvent()
            elif event.button() == Qt.RightButton:
                self.rwi.RightButtonReleaseEvent()
            elif event.button() == Qt.MidButton:
                self.rwi.MiddleButtonReleaseEvent()

    def __processMouseMoveEvent(self, event: QMouseEvent):
        ctrl, shift = self.__getCtrlShift(event)
        self.__setEventInformation(event.position(), ctrl, shift, chr(0), 0, None)
        self.rwi.MouseMoveEvent()

    def __processWheelEvent(self, event: QWheelEvent):
        ctrl, shift = self.__getCtrlShift(event)
        self.__setEventInformation(event.position(), ctrl, shift, chr(0), 0, None)

        delta = event.angleDelta().y()
        if delta > 0:
            self.rwi.MouseWheelForwardEvent()
        elif delta < 0:
            self.rwi.MouseWheelBackwardEvent()

    def __setEventInformation(self, positionPoint: QPointF, ctrl, shift, key, repeat=0, keysum=None):
        scale = self.__getPixelRatio()
        if self.__fbo.mirrorVertically():
            (w, h) = self.rw.GetSize()
            y = h - positionPoint.y()
            x = positionPoint.x()

        self.rwi.SetEventInformation(
            int(round(x * scale)),
            int(round(y * scale)),
            ctrl,
            shift,
            key,
            repeat,
            keysum,
        )

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
