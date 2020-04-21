from PySide2.QtCore import QObject, QUrl, qDebug, qCritical, Signal, Property, Slot
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType, QQmlEngine
from PySide2.QtWidgets import QApplication

from QVTKFramebufferObjectItem import FboItem
from CommandModelTranslate import TranslateParams_t
from ProcessingEngine import ProcessingEngine

class CanvasHandler(QObject):
    showFileDialogChanged = Signal(bool)
    isModelSelectedChanged = Signal(bool)
    selectedModelPositionXChanged = Signal(float)
    selectedModelPositionYChanged = Signal(float)

    def __init__(self, sys_argv):
        super().__init__()
        self.__previousWorldX:float = 0.0
        self.__previousWorldY:float = 0.0
        self.__draggingMouse:bool = False
        self.__showFileDialog:bool = False
        self.__vtkFboItem = None
        #* Set style: https://stackoverflow.com/questions/43093797/PySide2-quickcontrols-material-style
        sys_argv += ['--style', 'material'] #! MUST HAVE
        app = QApplication(sys_argv)

        engine = QQmlApplicationEngine()
        # engine.setImportPathList(['C:\\Users\\tungdao\\.conda\\envs\\qtvtkpy\\Lib\\site-packages\\PySide2\\qml'])
        # print(engine.importPathList())
        app.setApplicationName('QtVTK-Py')

        # #* Create classes instances
        self.__processingEngine = ProcessingEngine()

        # #* Expose/Bind Python classes (QObject) to QML
        ctxt = engine.rootContext() # returns QQmlContext
        ctxt.setContextProperty('canvasHandler', self)

        # #* Load main QML file
        engine.load(QUrl.fromLocalFile('resources\\main.qml'))

        # #* Get reference to the QVTKFramebufferObjectItem in QML
        rootObject = engine.rootObjects()[0] # returns QObject
        self.__vtkFboItem = rootObject.findChild(FboItem, 'vtkFboItem')

        # # #* Give the vtkFboItem reference to the CanvasHandler
        if (self.__vtkFboItem):
            qDebug('CanvasHandler::CanvasHandler: setting vtkFboItem to CanvasHandler')
            self.__vtkFboItem.setProcessingEngine(self.__processingEngine)

            self.__vtkFboItem.rendererInitialized.connect(self.startApplication)
            self.__vtkFboItem.isModelSelectedChanged.connect(self.isModelSelectedChanged)
            self.__vtkFboItem.selectedModelPositionXChanged.connect(self.selectedModelPositionXChanged)
            self.__vtkFboItem.selectedModelPositionYChanged.connect(self.selectedModelPositionYChanged)
        else:
            qCritical('CanvasHandler::CanvasHandler: Unable to get vtkFboItem instance')
            return

        rc = app.exec_()
        qDebug(f'CanvasHandler::CanvasHandler: Execution finished with return code: {rc}')

    def get_showFileDialog(self) -> bool:
        return self.__showFileDialog

    def set_showFileDialog(self, val:bool):
        if self.__showFileDialog == val:
            return
        self.__showFileDialog = val
        self.showFileDialogChanged.emit(val)

    #! PySide2 has limitations with the Property decorator, its setter since it is not recognized by QML
    #! https://stackoverflow.com/questions/57742024/custom-object-referencing-in-qml-python
    showFileDialog = Property(bool, fget=get_showFileDialog, fset=set_showFileDialog, notify=showFileDialogChanged)

    def get_isModelSelected(self) -> bool:
        return self.getIsModelSelected()

    isModelSelected = Property(bool, fget=get_isModelSelected, fset=None, notify=isModelSelectedChanged)

    def get_modelPositionX(self):
        return self.getSelectedModelPositionX()

    modelPositionX = Property(float, fget=get_modelPositionX, fset=None, notify=selectedModelPositionXChanged)

    def get_modelPositionY(self):
        return self.getSelectedModelPositionY()

    modelPositionY = Property(float, fget=get_modelPositionY, fset=None, notify=selectedModelPositionYChanged)

    @Slot(str)
    def openModel(self, path):
        qDebug(f'CanvasHandler::openModel(): {path}')
        qurl = QUrl(path) # don't use fromLocalFile (it will add file:/// as prefix)
        localFilePath = None
        if (qurl.isLocalFile()):
		    # Remove the "file:///" if present
            localFilePath = qurl.toLocalFile()
        else:
            localFilePath = qurl
        self.__vtkFboItem.addModelFromFile(localFilePath)

    @Slot(int,int,int)
    def mousePressEvent(self, button:int, screenX:int, screenY:int):
        qDebug('CanvasHandler::mousePressEvent()')
        self.__vtkFboItem.selectModel(screenX, screenY)

    @Slot(int,int,int)
    def mouseMoveEvent(self, button:int, screenX:int, screenY:int):
        if not self.__vtkFboItem.isModelSelected():
            return

        if not self.__draggingMouse:
            self.__draggingMouse = True
            self.__previousWorldX = self.__vtkFboItem.getSelectedModelPositionX()
            self.__previousWorldY = self.__vtkFboItem.getSelectedModelPositionY()

        translateParams = TranslateParams_t()
        translateParams.screenX = screenX
        translateParams.screenY = screenY
        self.__vtkFboItem.translateModel(translateParams, True)

    @Slot(int,int,int)
    def mouseReleaseEvent(self, button:int, screenX:int, screenY:int):
        qDebug('CanvasHandler::mouseReleaseEvent()')
        if not self.__vtkFboItem.isModelSelected():
            return

        if self.__draggingMouse:
            self.__draggingMouse = False
            translateParams = TranslateParams_t()
            translateParams.screenX = screenX
            translateParams.screenY = screenY
            translateParams.previousPositionX = self.__previousWorldX
            translateParams.previousPositionY = self.__previousWorldY
            self.__vtkFboItem.translateModel(translateParams, False)

    @Slot(int)
    def setModelsRepresentation(self, representationOption:int):
        self.__vtkFboItem.setModelsRepresentation(representationOption)

    @Slot(float)
    def setModelsOpacity(self, opacity:float):
        self.__vtkFboItem.setModelsOpacity(opacity)

    @Slot(bool)
    def setGouraudInterpolation(self, gouraudInterpolation:bool):
        self.__vtkFboItem.setGouraudInterpolation(gouraudInterpolation)

    @Slot(int)
    def setModelColorR(self, colorR:int):
        self.__vtkFboItem.setModelColorR(colorR)

    @Slot(int)
    def setModelColorG(self, colorG:int):
        self.__vtkFboItem.setModelColorG(colorG)

    @Slot(int)
    def setModelColorB(self, colorB:int):
        self.__vtkFboItem.setModelColorB(colorB)


    def startApplication(self):
        qDebug('CanvasHandler::startApplication()')
        self.__vtkFboItem.rendererInitialized.disconnect(self.startApplication)


    def getIsModelSelected(self) -> bool:
        #* QVTKFramebufferObjectItem might not be initialized when QML loads
        if not self.__vtkFboItem:
            return False
        return self.__vtkFboItem.isModelSelected()

    def getSelectedModelPositionX(self) -> float:
	    #* QVTKFramebufferObjectItem might not be initialized when QML loads
        if not self.__vtkFboItem:
            return 0
        return self.__vtkFboItem.getSelectedModelPositionX()

    def getSelectedModelPositionY(self) -> float:
        #* QVTKFramebufferObjectItem might not be initialized when QML loads
        if not self.__vtkFboItem:
            return 0
        return self.__vtkFboItem.getSelectedModelPositionY()


    def __isModelExtensionValid(self, modelPath:QUrl) -> bool:
        if modelPath.toString().toLower().endsWith('.stl') or modelPath.toString().toLower().endsWith('.obj'):
            return True
        else:
            return False
