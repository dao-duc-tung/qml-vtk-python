from PySide2.QtCore import QObject, QUrl, qDebug, qCritical, Signal, Property, Slot
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType, QQmlEngine
from PySide2.QtWidgets import QApplication

from src.pieces.graphics import FboItem
# from CommandModelTranslate import TranslateParams_t
# from ProcessingEngine import ProcessingEngine

class MainCtrl(QObject):
    # showFileDialogChanged = Signal(bool)
    # isModelSelectedChanged = Signal(bool)
    # selectedModelPositionXChanged = Signal(float)
    # selectedModelPositionYChanged = Signal(float)

    def __init__(self):
        super().__init__()
        # self.__previousWorldX:float = 0.0
        # self.__previousWorldY:float = 0.0
        # self.__draggingMouse:bool = False
        # self.__showFileDialog:bool = False
        self.__fboItem = None

        self.__engine = QQmlApplicationEngine()
        self.__engine.load(QUrl.fromLocalFile(f":/main.qml"))
        # self.__engine.setImportPathList(['C:\\Users\\tungdao\\.conda\\envs\\QmlVtkpy\\Lib\\site-packages\\PySide2\\qml'])
        # print(self.__engine.importPathList())

        # self.__processingEngine = ProcessingEngine()

        # ctxt = self.__engine.rootContext() # returns QQmlContext
        # ctxt.setContextProperty('canvasHandler', self)

        # rootObject = self.__engine.rootObjects()[0] # returns QObject
        # self.__fboItem = rootObject.findChild(FboItem, 'fboItem')

        # if (self.__fboItem):
        #     qDebug('CanvasHandler::CanvasHandler: setting vtkFboItem to CanvasHandler')
        #     self.__fboItem.setProcessingEngine(self.__processingEngine)

        #     self.__fboItem.rendererInitialized.connect(self.startApplication)
        #     self.__fboItem.isModelSelectedChanged.connect(self.isModelSelectedChanged)
        #     self.__fboItem.selectedModelPositionXChanged.connect(self.selectedModelPositionXChanged)
        #     self.__fboItem.selectedModelPositionYChanged.connect(self.selectedModelPositionYChanged)
        # else:
        #     qCritical('CanvasHandler::CanvasHandler: Unable to get vtkFboItem instance')
        #     return

    # def get_showFileDialog(self) -> bool:
    #     return self.__showFileDialog

    # def set_showFileDialog(self, val:bool):
    #     if self.__showFileDialog == val:
    #         return
    #     self.__showFileDialog = val
    #     self.showFileDialogChanged.emit(val)

    # showFileDialog = Property(bool, fget=get_showFileDialog, fset=set_showFileDialog, notify=showFileDialogChanged)

    # def get_isModelSelected(self) -> bool:
    #     return self.getIsModelSelected()

    # isModelSelected = Property(bool, fget=get_isModelSelected, fset=None, notify=isModelSelectedChanged)

    # def get_modelPositionX(self):
    #     return self.getSelectedModelPositionX()

    # modelPositionX = Property(float, fget=get_modelPositionX, fset=None, notify=selectedModelPositionXChanged)

    # def get_modelPositionY(self):
    #     return self.getSelectedModelPositionY()

    # modelPositionY = Property(float, fget=get_modelPositionY, fset=None, notify=selectedModelPositionYChanged)

    # @Slot(str)
    # def openModel(self, path):
    #     qDebug(f'CanvasHandler::openModel(): {path}')
    #     qurl = QUrl(path) # don't use fromLocalFile (it will add file:/// as prefix)
    #     localFilePath = None
    #     if (qurl.isLocalFile()):
	# 	    # Remove the "file:///" if present
    #         localFilePath = qurl.toLocalFile()
    #     else:
    #         localFilePath = qurl
    #     self.__fboItem.addModelFromFile(localFilePath)

    # @Slot(int,int,int)
    # def mousePressEvent(self, button:int, screenX:int, screenY:int):
    #     qDebug('CanvasHandler::mousePressEvent()')
    #     self.__fboItem.selectModel(screenX, screenY)

    # @Slot(int,int,int)
    # def mouseMoveEvent(self, button:int, screenX:int, screenY:int):
    #     if not self.__fboItem.isModelSelected():
    #         return

    #     if not self.__draggingMouse:
    #         self.__draggingMouse = True
    #         self.__previousWorldX = self.__fboItem.getSelectedModelPositionX()
    #         self.__previousWorldY = self.__fboItem.getSelectedModelPositionY()

    #     translateParams = TranslateParams_t()
    #     translateParams.screenX = screenX
    #     translateParams.screenY = screenY
    #     self.__fboItem.translateModel(translateParams, True)

    # @Slot(int,int,int)
    # def mouseReleaseEvent(self, button:int, screenX:int, screenY:int):
    #     qDebug('CanvasHandler::mouseReleaseEvent()')
    #     if not self.__fboItem.isModelSelected():
    #         return

    #     if self.__draggingMouse:
    #         self.__draggingMouse = False
    #         translateParams = TranslateParams_t()
    #         translateParams.screenX = screenX
    #         translateParams.screenY = screenY
    #         translateParams.previousPositionX = self.__previousWorldX
    #         translateParams.previousPositionY = self.__previousWorldY
    #         self.__fboItem.translateModel(translateParams, False)

    # @Slot(int)
    # def setModelsRepresentation(self, representationOption:int):
    #     self.__fboItem.setModelsRepresentation(representationOption)

    # @Slot(float)
    # def setModelsOpacity(self, opacity:float):
    #     self.__fboItem.setModelsOpacity(opacity)

    # @Slot(bool)
    # def setGouraudInterpolation(self, gouraudInterpolation:bool):
    #     self.__fboItem.setGouraudInterpolation(gouraudInterpolation)

    # @Slot(int)
    # def setModelColorR(self, colorR:int):
    #     self.__fboItem.setModelColorR(colorR)

    # @Slot(int)
    # def setModelColorG(self, colorG:int):
    #     self.__fboItem.setModelColorG(colorG)

    # @Slot(int)
    # def setModelColorB(self, colorB:int):
    #     self.__fboItem.setModelColorB(colorB)


    # def startApplication(self):
    #     qDebug('CanvasHandler::startApplication()')
    #     self.__fboItem.rendererInitialized.disconnect(self.startApplication)


    # def getIsModelSelected(self) -> bool:
    #     #* QVTKFramebufferObjectItem might not be initialized when QML loads
    #     if not self.__fboItem:
    #         return False
    #     return self.__fboItem.isModelSelected()

    # def getSelectedModelPositionX(self) -> float:
	#     #* QVTKFramebufferObjectItem might not be initialized when QML loads
    #     if not self.__fboItem:
    #         return 0
    #     return self.__fboItem.getSelectedModelPositionX()

    # def getSelectedModelPositionY(self) -> float:
    #     #* QVTKFramebufferObjectItem might not be initialized when QML loads
    #     if not self.__fboItem:
    #         return 0
    #     return self.__fboItem.getSelectedModelPositionY()


    # def __isModelExtensionValid(self, modelPath:QUrl) -> bool:
    #     if modelPath.toString().toLower().endsWith('.stl') or modelPath.toString().toLower().endsWith('.obj'):
    #         return True
    #     else:
    #         return False
