import abc

class Handler():
    def __init__(self):
        pass

    @abc.abstractmethod
    def handle(self,event,context):
        pass
