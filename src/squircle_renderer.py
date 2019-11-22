# -*- coding: utf-8 -*-

from PySide2 import QtCore, QtGui, QtQuick
import logging
import threading

from OpenGL import GL

class SquircleRenderer( QtCore.QObject ):
    def __init__( self ):
        logging.debug(threading.get_ident())
        logging.debug('SquircleRenderer.__init__')
        super().__init__()

        # self.profile = QtGui.QOpenGLVersionProfile()
        # self.profile.setVersion( 2, 1 )
        self.gl = QtGui.QOpenGLFunctions()
        self.viewportSize = QtCore.QSize()
        self.t = 0.0
        self.program = None
        self.window = None

    def setT( self, t ):
        self.t = t

    def setViewportSize( self, size ):
        logging.debug(threading.get_ident())
        logging.debug('SquircleRenderer.setViewportSize')
        self.viewportSize = size

    def setWindow( self, window ):
        logging.debug(threading.get_ident())
        logging.debug('SquircleRenderer.setWindow')
        self.window = window

    def initialize( self ):
        logging.debug(threading.get_ident())
        logging.debug('SquircleRenderer.initialize')
        logging.debug(self.window)
        if self.window != None:
            # self.gl = self.window.openglContext().versionFunctions( self.profile )

            self.program = QtGui.QOpenGLShaderProgram()
            self.program.addCacheableShaderFromSourceCode( QtGui.QOpenGLShader.Vertex, "attribute highp vec4 vertices;varying highp vec2 coords;void main() { gl_Position = vertices; coords = vertices.xy;}" )
            self.program.addCacheableShaderFromSourceCode( QtGui.QOpenGLShader.Fragment, "uniform lowp float t; varying highp vec2 coords; void main() { lowp float i = 1. - (pow(abs(coords.x), 4.) + pow(abs(coords.y), 4.)); i = smoothstep(t - 0.8, t + 0.8, i); i = floor(i * 20.) / 20.; gl_FragColor = vec4(coords * .5 + .5, i, i);}" )
            self.program.bindAttributeLocation( "vertices", 0 )
            self.program.link()
            logging.debug(threading.get_ident())
            logging.debug('SquircleRenderer.initialize inside if')
            logging.debug(self.program)

    def render( self ):
        logging.debug(threading.get_ident())
        logging.debug('SquircleRenderer.render')
        logging.debug('after SquircleRenderer.render')
        logging.debug(self.program)
        if self.program == None:
            logging.debug('self.program None!')
            self.initialize()
        logging.debug('SquircleRenderer.render 1')
        self.gl.initializeOpenGLFunctions()
        self.gl.glUseProgram(0)
        self.gl.glClearColor( 0, 0, 0, 1 )
        self.gl.glClear( GL.GL_COLOR_BUFFER_BIT )
        self.gl.glDisable( GL.GL_DEPTH_TEST )

        # values = [ [ -1.0, -1.0 ], [ 1.0, -1.0 ], [ -1.0, 1.0 ], [ 1.0, 1.0 ] ]
        import numpy as np
        values = np.array([
            (-1.0, -1.0),
            (1.0, -1.0),
            (-1.0, 1.0),
            (1.0, 1.0)
        ], dtype='f')
        logging.debug(values)

        logging.debug('SquircleRenderer.render 2')
        self.program.bind()
        self.program.enableAttributeArray( 0 )
        self.program.setAttributeArray( 0, GL.GL_FLOAT, values.tobytes(), 2 ) #! IMPORTANT
        self.program.setUniformValue( 't', self.t, self.t )

        logging.debug('SquircleRenderer.render 3')
        self.gl.glEnable( GL.GL_BLEND )
        self.gl.glBlendFunc( GL.GL_SRC_ALPHA, GL.GL_ONE )

        logging.debug('SquircleRenderer.render 4')
        self.gl.glDrawArrays( GL.GL_TRIANGLE_STRIP, 0, 4 )

        logging.debug('SquircleRenderer.render 5')
        self.program.disableAttributeArray( 0 )
        self.program.release()
        logging.debug('SquircleRenderer.render 6')
        self.window.resetOpenGLState()
        logging.debug('SquircleRenderer.render 7')
