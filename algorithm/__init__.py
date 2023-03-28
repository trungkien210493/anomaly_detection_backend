from abc import ABC, abstractmethod

class BaseAlgorithm(ABC):
    
    @abstractmethod
    def __init__(self, config, data):
        self.data = data
        self.config = config
        super(BaseAlgorithm, self).__init__()
    
    @abstractmethod
    def detect(self):
        pass

    def kind(self):
        return self.__class__.__name__

