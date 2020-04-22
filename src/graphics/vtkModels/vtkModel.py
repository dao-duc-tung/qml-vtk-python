from PySide2.QtCore import QObject, QUrl, qDebug, qCritical, QFileInfo, QThread, Signal


class VtkModel(QObject):
    @property
    def model(self):
        raise NotImplementedError()

    def __init__(self, name: str):
        super().__init__()
        self.name = name
