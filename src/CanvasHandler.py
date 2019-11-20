from PyQt5.QtCore import QObject, QApp, QUrl, qDebug, qCritical, pyqtSignal
from PyQt5.QtQml import QQmlApplicationEngine, qmlRegisterType
from PyQt5.QtWidgets import QApplication

from .QVTKFramebufferObjectItem import QVTKFramebufferObjectItem
from .CommandModelTranslate import TranslateParams_t
from .ProcessingEngine import ProcessingEngine

class CanvasHandler(QObject):
    showFileDialogChanged = pyqtSignal()
	isModelSelectedChanged = pyqtSignal()
	selectedModelPositionXChanged = pyqtSignal()
	selectedModelPositionYChanged = pyqtSignal()

    def __init__(self, sys_argv):
        self.__m_previousWorldX:float = 0.0
        self.__m_previousWorldY:float = 0.0
        self.__m_draggingMouse:bool = False
        self.__m_showFileDialog:bool = False
        #* Set style: https://stackoverflow.com/questions/43093797/pyqt5-quickcontrols-material-style
        sys_argv += ['--style', 'material']
        app = QApplication(sys_argv)
        engine = QQmlApplicationEngine()
        app.setApplicationName('QtVTK-Py')

        #* Register QML Types
        qmlRegisterType(QVTKFramebufferObjectItem, 'QtVTK', 1, 0, 'VtkFboItem')

        #* Create classes instances
        self.__m_processingEngine = ProcessingEngine()

        #* Expose/Bind Python classes (QObject) to QML
        ctxt = engine.rootContext() # this returns QQmlContext
        ctxt.setContextProperty('canvasHandler', this)

        #* Load main QML file
        engine.load(QUrl.fromLocalFile('/resources/main.qml'))

        #* Get reference to the QVTKFramebufferObjectItem in QML
        rootObject = engine.rootObjects()[0] # this returns QObject
        self.__m_vtkFboItem:QVTKFramebufferObjectItem = rootObject.findChild('vtkFboItem')

        #* Give the vtkFboItem reference to the CanvasHandler
        if (self.__m_vtkFboItem):
            qDebug('CanvasHandler::CanvasHandler: setting vtkFboItem to CanvasHandler')
            self.__m_vtkFboItem.setProcessingEngine(self.__m_processingEngine)

            self.__m_vtkFboItem.rendererInitialized.connect(self.startApplication)
            self.__m_vtkFboItem.isModelSelectedChanged.connect(self.isModelSelectedChanged)
            self.__m_vtkFboItem.selectedModelPositionXChanged.connect(self.selectedModelPositionXChanged)
            self.__m_vtkFboItem.selectedModelPositionYChanged.connect(self.selectedModelPositionYChanged)
        else:
		    qCritical('CanvasHandler::CanvasHandler: Unable to get vtkFboItem instance')
            return

        rc = app.exec()
        qDebug(f'CanvasHandler::CanvasHandler: Execution finished with return code: {rc}')

    def startApplication(self):
        qDebug('CanvasHandler::startApplication()')
        self.__m_vtkFboItem.rendererInitialized.disconnect(self.startApplication)

    def openModel(self, path:QUrl):
        qDebug(f'CanvasHandler::openModel(): {path}')
        localFilePath = None
        if (path.isLocalFile()):
            localFilePath = path.toLocalFile()
        else:
            localFilePath = path
        self.__m_vtkFboItem.addModelFromFile(localFilePath)

    def __isModelExtensionValid(self, modelPath:QUrl) -> bool:
        if modelPath.toString().toLower().endsWith('.stl') or modelPath.toString().toLower().endsWith('.obj'):
            return True
        else:
            return False

    def mousePressEvent(self, button:int, screenX:int, screenY:int):
    	qDebug('CanvasHandler::mousePressEvent()')
	    self.__m_vtkFboItem.selectModel(screenX, screenY)

    def mouseMoveEvent(self, button:int, screenX:int, screenY:int)
        if not self.__m_vtkFboItem.isModelSelected()
            return

        if not self.__m_draggingMouse
            self.__m_draggingMouse = True
            self.__m_previousWorldX = self.__m_vtkFboItem.getSelectedModelPositionX()
            self.__m_previousWorldY = self.__m_vtkFboItem.getSelectedModelPositionY()

        translateParams = TranslateParams_t()
        translateParams.screenX = screenX
        translateParams.screenY = screenY
        self.__m_vtkFboItem.translateModel(translateParams, True)

    def mouseReleaseEvent(self, button:int, screenX:int, screenY:int)
        qDebug('CanvasHandler::mouseReleaseEvent()')
        if not self.__m_vtkFboItem.isModelSelected():
            return

        if self.__m_draggingMouse
            self.__m_draggingMouse = False
            translateParams = TranslateParams_t()
            translateParams.screenX = screenX
            translateParams.screenY = screenY
            translateParams.previousPositionX = m_previousWorldX
            translateParams.previousPositionY = m_previousWorldY
            self.__m_vtkFboItem.translateModel(translateParams, False)


    def getIsModelSelected(self) -> bool:
        #* QVTKFramebufferObjectItem might not be initialized when QML loads
        if not self.__m_vtkFboItem
            return 0
        return self.__m_vtkFboItem.isModelSelected()

    def getSelectedModelPositionX(self) -> float:
	    #* QVTKFramebufferObjectItem might not be initialized when QML loads
        if not self.__m_vtkFboItem
            return 0
        return self.__m_vtkFboItem.getSelectedModelPositionX()

    def getSelectedModelPositionY(self) -> float:
        #* QVTKFramebufferObjectItem might not be initialized when QML loads
        if not self.__m_vtkFboItem
            return 0
        return self.__m_vtkFboItem.getSelectedModelPositionY()

    def setModelsRepresentation(self, representationOption:int):
    	self.__m_vtkFboItem.setModelsRepresentation(representationOption)

    def setModelsOpacity(self, opacity:float):
    	self.__m_vtkFboItem.setModelsOpacity(opacity)

    def setGouraudInterpolation(self, gouraudInterpolation:bool):
    	self.__m_vtkFboItem.setGouraudInterpolation(gouraudInterpolation)

    def setModelColorR(self, colorR:int):
    	self.__m_vtkFboItem.setModelColorR(colorR)

    def setModelColorG(self, colorG:int):
    	self.__m_vtkFboItem.setModelColorG(colorG)

    def setModelColorB(self, colorB:int):
    	self.__m_vtkFboItem.setModelColorB(colorB)
