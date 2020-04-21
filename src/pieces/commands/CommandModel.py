class CommandModel():
    def isReady(self) -> bool:
        raise NotImplementedError()

    def execute(self):
        raise NotImplementedError()
