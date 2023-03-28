from . import BaseAlgorithm


class TSDecomposition(BaseAlgorithm):

    def __init__(self, config, data):
        """Time Series decomposition method

        Args:
            config (dict): the tuning argument for the algorithm
            data (list): the data input from grafana. A list contains only 2 arrays: one time array and one values array
        """
        super(TSDecomposition, self).__init__(config, data)
    
    def detect(self):
        pass