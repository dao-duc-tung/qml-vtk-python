from abc import ABC, ABCMeta, abstractmethod

from QVTKFramebufferObjectRenderer import QVTKFramebufferObjectRenderer

class CommandModel():
    @property
    @abstractmethod
    def _m_vtkFboRenderer(self) -> QVTKFramebufferObjectRenderer:
        return QVTKFramebufferObjectRenderer()

    @abstractmethod
    def isReady(self) -> bool:
        pass

    @abstractmethod
    def execute(self):
        pass
