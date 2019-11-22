from abc import ABC, ABCMeta, abstractmethod

from QVTKFramebufferObjectRenderer import SquircleInFboRenderer

class CommandModel():
    @abstractmethod
    def isReady(self) -> bool:
        pass

    @abstractmethod
    def execute(self):
        pass
