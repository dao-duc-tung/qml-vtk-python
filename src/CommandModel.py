from abc import ABC, ABCMeta, abstractmethod

from QVTKFramebufferObjectRenderer import SquircleInFboRenderer

class CommandModel():
    def isReady(self) -> bool:
        raise Exception('Not implemented')

    def execute(self):
        raise Exception('Not implemented')
