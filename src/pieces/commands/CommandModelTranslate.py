from Model import Model
from CommandModel import CommandModel

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
    def __init__(self, vtkFboRenderer, translateData:TranslateParams_t, inTransition:bool):
        self.__translateParams:TranslateParams_t = translateData
        self.__inTransition:bool = inTransition
        self.__needsTransformation:bool = True
        self.__vtkFboRenderer = vtkFboRenderer

    def isReady(self) -> bool:
        return True

    def __transformCoordinates(self):
        worldCoordinates = [0.0, 0.0, 0.0]

        if self.__vtkFboRenderer.renderer.screenToWorld(self.__translateParams.screenX, self.__translateParams.screenY, worldCoordinates):
            self.__translateParams.targetPositionX = worldCoordinates[0] - self.__translateParams.model.getMouseDeltaX()
            self.__translateParams.targetPositionY = worldCoordinates[1] - self.__translateParams.model.getMouseDeltaY()

        else:
            self.__translateParams.targetPositionX = self.__translateParams.model.getPositionX()
            self.__translateParams.targetPositionY = self.__translateParams.model.getPositionY()

        self.__needsTransformation = False

    def execute(self):
        if self.__needsTransformation:
            self.__transformCoordinates()

        self.__translateParams.model.translateToPosition(self.__translateParams.targetPositionX, self.__translateParams.targetPositionY)
