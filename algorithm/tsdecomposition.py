from . import BaseAlgorithm
import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose


class TSDecomposition(BaseAlgorithm):

    def __init__(self, config, data):
        """Time Series decomposition method

        Args:
            config (dict): the tuning argument for the algorithm
            data (list): the data input from grafana. A list contains only 2 arrays: one time array and one values array
        """
        super(TSDecomposition, self).__init__(config, data)
    
    def detect(self):
        # Init input - Start
        model = "additive"
        period = 7
        threshold = 3
        show_bound = False
        if "model" in self.config:
            model = self.config['model']
        if "period" in self.config:
            period = self.config['period']
        if "threshold" in self.config:
            threshold = self.config["threshold"]
        if "show_bound" in self.config:
            show_bound = self.config["show_bound"]
        # Init input - End
        df = pd.DataFrame({'time': self.data[0], 'data': self.data[1]})
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        df.set_index("time", inplace=True)
        ds_result = seasonal_decompose(df, model=model, period=period)
        resid = ds_result.resid
        upper, lower = [resid.mean() + threshold * resid.std(), resid.mean() - threshold * resid.std()]
        df['upper'] = ds_result.trend + ds_result.seasonal + upper
        df['lower'] = ds_result.trend + ds_result.seasonal + lower
        df.dropna(inplace=True)
        df.index = df.index.view(np.int64)//10**6
        anomaly = df[(df['data'] < df['lower']) | (df['data'] > df['upper'])]['data']
        return_value = {}
        if len(anomaly) == 0:
            return_value['anomaly'] = {}
        else:
            return_value['anomaly'] = anomaly.to_dict()
        if show_bound:
            return_value['upper'] = df['upper'].to_dict()
            return_value['lower'] = df['lower'].to_dict()
        return return_value