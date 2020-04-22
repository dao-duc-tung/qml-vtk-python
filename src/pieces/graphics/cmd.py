class Cmd:
    def __init__(self, callback, **kwargs):
        self.__callback = callback
        self.__kwargs = kwargs

    def execute(self):
        self.__callback(self.__kwargs)
