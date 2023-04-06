from . import BaseAlgorithm
import pandas as pd
import numpy as np
from statsmodels.tsa.api import ExponentialSmoothing


class HoltWinter(BaseAlgorithm):

    def __init__(self, config, data):
        """Holt-Winter method

        Args:
            config (dict): the tuning argument for the algorithm
            data (list): the data input from grafana. A list contains only 2 arrays: one time array and one values array
        """
        super(HoltWinter, self).__init__(config, data)
    
    def detect(self):
        """
        Detect anomaly based on argument in "config" attribute
        """
        # Init input - Start
        trend = "add"
        seasonal = "add"
        seasonal_periods = None
        damped_trend = False
        use_boxcox = False
        threshold = 3
        show_bound = False
        if "trend" in self.config:
            trend = self.config["trend"]
        if "seasonal" in self.config:
            seasonal = self.config["seasonal"]
        if "seasonal_periods" in self.config:
            seasonal_periods = self.config["seasonal_periods"]
        if "damped_trend" in self.config:
            damped_trend = self.config["damped_trend"]
        if "use_boxcox" in self.config:
            use_boxcox = self.config["use_boxcox"]
        if "threshold" in self.config:
            threshold = self.config["threshold"]
        if "show_bound" in self.config:
            show_bound = self.config["show_bound"]
        # Init input - End
        df = pd.DataFrame({'time': self.data[0], 'data': self.data[1]})
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        df.set_index("time", inplace=True)
        model = ExponentialSmoothing(df, seasonal_periods=seasonal_periods, trend=trend, seasonal=seasonal,
                                    damped_trend=damped_trend, use_boxcox=use_boxcox).fit()
        resid = model.resid
        upper, lower = [resid.mean() + threshold * resid.std(), resid.mean() - threshold * resid.std()]
        df['upper'] = model.fittedvalues + upper
        df['lower'] = model.fittedvalues + lower
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
