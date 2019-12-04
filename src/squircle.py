# -*- coding: utf-8 -*-

from PySide2 import QtCore, QtGui, QtQuick
import squircle_renderer
import logging
import threading

logging.basicConfig(filename='log.ini', level=logging.DEBUG)

class SquircleInFboRenderer( QtQuick.QQuickFramebufferObject.Renderer ):
    def __init__( self ):
        logging.debug(threading.get_ident())
        logging.debug('SquircleInFboRenderer.__init__')
        super().__init__()

        self.squircle = squircle_renderer.SquircleRenderer()
        self.squircle.initialize()

    def render( self ):
        logging.debug(threading.get_ident())
        logging.debug('SquircleInFboRenderer.render')
        self.squircle.render()
        self.update()

    def createFrameBufferObject( self, size ):
        logging.debug(threading.get_ident())
        logging.debug('SquircleInFboRenderer.createFrameBufferObject')
        format = QtGui.QOpenGLFramebufferObjectFormat()
        format.setAttachment( QtGui.QOpenGLFramebufferObject.CombinedDepthStencil )
        format.setSamples( 4 )
        return QtGui.QOpenGLFramebufferObject( size, format )

class Squircle( QtQuick.QQuickFramebufferObject ):
    tChanged = QtCore.Signal(float)

    def __init__( self, parent=None ):
        logging.debug(threading.get_ident())
        logging.debug('Squircle.__init__')
        super().__init__( parent )

        self.renderer = None

    def gett( self ):
        if self.renderer == None:
            return 0.0
        else:
            return self.renderer.squircle.t

    def sett( self, value ):
        if self.renderer == None or self.renderer.squircle.t == value:
            return
        self.renderer.squircle.setT( value )
        self.tChanged.emit(value)
        if self.window():
            self.window().update()

    t = QtCore.Property(float, fget=gett, fset=sett, notify=tChanged)

    def createRenderer( self ):
        logging.debug(threading.get_ident())
        logging.debug('Squircle.createRenderer')
        self.renderer = SquircleInFboRenderer()
        logging.debug(threading.get_ident())
        logging.debug('set window inside Squircle.createRenderer')
        self.renderer.squircle.setWindow( self.window() )
        return self.renderer
