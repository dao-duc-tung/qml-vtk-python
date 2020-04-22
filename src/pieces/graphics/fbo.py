from typing import List, Optional

from PySide2.QtCore import (
    QEvent,
    QPointF,
    Qt,
    Slot,
)
from PySide2.QtGui import QMouseEvent
from PySide2.QtQuick import QQuickFramebufferObject

import vtk
from src.pieces import graphics
from src.utils import *


class Fbo(QQuickFramebufferObject):
    @property
    def rw(self) -> vtk.vtkExternalOpenGLRenderWindow:
        return self.__fbo_renderer.rw

    @property
    def rwi(self) -> vtk.vtkGenericRenderWindowInteractor:
        return self.__fbo_renderer.rwi

    def __init__(self):
        super().__init__()
        self.__fbo_renderer: graphics.FboRenderer = None

        self.lastMouseButtonEvent: QMouseEvent = None
        self.lastMouseMoveEvent: QMouseEvent = None
        self.lastWheelEvent: QWheelEvent = None

        self.setAcceptedMouseButtons(Qt.AllButtons)
        self.setMirrorVertically(True)

    def createRenderer(self) -> QQuickFramebufferObject.Renderer:
        self.__fbo_renderer = graphics.FboRenderer()
        return self.__fbo_renderer

    def addCommand(self, command: "commands.Command"):
        with self.__fbo_renderer.commandQueueLock:
            self.__fbo_renderer.commandQueue.put(command)
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        self.__processMouseButtonEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.__processMouseButtonEvent(event)

    def __processMouseButtonEvent(self, event: QMouseEvent):
        self.lastMouseButtonEvent = cloneMouseEvent(event)
        self.lastMouseButtonEvent.ignore()
        event.accept()
        self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        self.lastMouseMoveEvent = cloneMouseEvent(event)
        self.lastMouseMoveEvent.ignore()
        event.accept()
        self.update()

    def wheelEvent(self, event: QWheelEvent):
        self.lastWheelEvent = cloneWheelEvent(event)
        self.lastWheelEvent.ignore()
        event.accept()
        self.update()

    @Slot(float, float, int, int, int)
    def onMousePressed(
        self, x: float, y: float, button: int, buttons: int, modifiers: int
    ):
        self.lastMouseButtonEvent = convertToMouseEvent(
            QEvent.MouseButtonPress,
            QPointF(x, y),
            Qt.MouseButton(button),
            Qt.MouseButtons(buttons),
            Qt.KeyboardModifiers(modifiers),
        )
        self.lastMouseButtonEvent.ignore()
        self.update()

    @Slot(float, float, int, int, int)
    def onMouseReleased(
        self, x: float, y: float, button: int, buttons: int, modifiers: int
    ):
        self.lastMouseButtonEvent = convertToMouseEvent(
            QEvent.MouseButtonRelease,
            QPointF(x, y),
            Qt.MouseButton(button),
            Qt.MouseButtons(buttons),
            Qt.KeyboardModifiers(modifiers),
        )
        self.lastMouseButtonEvent.ignore()
        self.update()

    @Slot(float, float, int, int, int)
    def onMouseMove(
        self, x: float, y: float, button: int, buttons: int, modifiers: int
    ):
        self.lastMouseMoveEvent = convertToMouseEvent(
            QEvent.MouseMove,
            QPointF(x, y),
            Qt.MouseButton(button),
            Qt.MouseButtons(buttons),
            Qt.KeyboardModifiers(modifiers),
        )
        self.lastMouseMoveEvent.ignore()
        self.update()
