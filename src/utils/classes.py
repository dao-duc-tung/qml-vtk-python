from multiprocessing import Lock
from PySide2.QtCore import QObject


# Thread-safe Singleton
class Singleton(type):
    def __new__(mcs, name, bases, attrs):
        cls = super(Singleton, mcs).__new__(mcs, name, bases, attrs)
        cls.__sharedInstanceLock__ = Lock()
        return cls

    def __call__(cls, *args, **kwargs):
        with cls.__sharedInstanceLock__:
            try:
                return cls.__sharedInstance__
            except AttributeError:
                cls.__sharedInstance__ = super(Singleton, cls).__call__(*args, **kwargs)
                return cls.__sharedInstance__


# Thread-safe Singleton
class SingletonQObjectMeta(type(QObject), Singleton):
    def __new__(mcs, name, bases, attrs):
        # Assume the target class is created (i.e. this method to be called) in the main thread.
        cls = type(QObject).__new__(mcs, name, bases, attrs)
        cls.__sharedInstanceLock__ = Lock()
        return cls
