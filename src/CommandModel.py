from abc import abstractmethod
from .QVTKFramebufferObjectRenderer import QVTKFramebufferObjectRenderer

class CommandModel():
    def __init__(self):
        self._m_vtkFboRenderer:QVTKFramebufferObjectRenderer = QVTKFramebufferObjectRenderer()

    @abstractmethod
    def isReady(self) -> bool:
        pass

    @abstractmethod
    def execute(self):
        pass
