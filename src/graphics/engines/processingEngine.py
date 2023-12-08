from typing import Dict

from src.graphics.vtkModels import *


class ProcessingEngine:
    """
    Manage VTK-related models
    """

    def __init__(self):
        self.__models: Dict[str, VtkModel] = {}

    def registerModel(self, model: VtkModel):
        print("register model: {}".format(model))
        self.__models[model.name] = model

    def getModel(self, name: str):
        print("get model: {}".format(name))
        if name in self.__models:
            return self.__models[name]

    def removeModel(self, name: str):
        if name in self.__models:
            del self.__models[name]
