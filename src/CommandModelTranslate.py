from Model import Model
from CommandModel import CommandModel
from QVTKFramebufferObjectRenderer import QVTKFramebufferObjectRenderer

class TranslateParams_t():
    def __init__(self):
        self.model:Model = None
        self.screenX:int = 0
        self.screenY:int = 0
        self.previousPositionX:float = 0.0
        self.previousPositionY:float = 0.0
        self.targetPositionX:float = 0.0
        self.targetPositionY:float = 0.0

class CommandModelTranslate(CommandModel):
    def __init__(self, vtkFboRenderer:QVTKFramebufferObjectRenderer, translateData:TranslateParams_t, inTransition:bool):
        self.__m_translateParams:TranslateParams_t = translateData
        self.__m_inTransition:bool = inTransition
        self.__m_needsTransformation:bool = True
        self._m_vtkFboRenderer:QVTKFramebufferObjectRenderer = vtkFboRenderer

    def isReady(self) -> bool:
        return True

    def __transformCoordinates(self):
        worldCoordinates = [0.0, 0.0, 0.0]

        if self._m_vtkFboRenderer.screenToWorld(self.__m_translateParams.screenX, self.__m_translateParams.screenY, worldCoordinates):
            self.__m_translateParams.targetPositionX = worldCoordinates[0] - self.__m_translateParams.model.getMouseDeltaX()
            self.__m_translateParams.targetPositionY = worldCoordinates[1] - self.__m_translateParams.model.getMouseDeltaY()

        else:
            self.__m_translateParams.targetPositionX = self.__m_translateParams.model.getPositionX()
            self.__m_translateParams.targetPositionY = self.__m_translateParams.model.getPositionY()

        self.__m_needsTransformation = False

    def execute(self):
        # Screen to world transformation can only be done within the Renderer thread
        if self.__m_needsTransformation:
            self.__transformCoordinates()

        self.__m_translateParams.model.translateToPosition(self.__m_translateParams.targetPositionX, self.__m_translateParams.targetPositionY)
