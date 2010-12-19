class FSignal(object):
    def __init__(self, *args):
        self.signature = args
        self.__callbacks = []

    def emit(self, *args):
        for i in self.__callbacks:
            i(*args)

    def connect(self, callback):
        self.__callbacks.append(callback)

    def __call__(self, *args):
        self.emit(*args)
