import os
from sanic.log import logger
from sanic import Sanic
from sanic.response import HTTPResponse
from sanic.request import Request
from sanic import json
from sanic_ext import Extend
from copy import deepcopy
from algorithm import holtwinter, tsdecomposition
import re


app = Sanic("AnomalyDetectionApp")
app.config.CORS_ORIGINS = '*'
Extend(app)

@app.get("/api/list")
async def list_handle(request: Request) -> HTTPResponse:
    return json([{"label": "Time Series Decomposition", "value": "tsdecomposition"}, 
                {"label": "Holt-Winter", "value": "holtwinter"}])

@app.post("/api/query")
async def anomaly_handle(request: Request) -> HTTPResponse:
    body = request.json
    return_value = body['data']
    # Init arguments - Start
    regex = '.*'
    config = {}
    method = 'tsdecomposition'
    if 'regex' in body:
        regex = body['regex']
    if 'config' in body:
        config = body['config']
    if 'method' in body:
        method = body['method']
    # Init arguments - End
    series = []
    for i in range(len(return_value['data'])):
        if "name" in return_value['data'][i]:
            # Hard code check name series in influxdb
            if re.match(regex, return_value['data'][i]['name']):
                series.append(return_value['data'][i])
        elif "datapoints" in return_value['data'][i]:
            # Hard code check name series in elasticsearch
            if re.match(regex, return_value['data'][i]['target']):
                series.append(return_value['data'][i])
        else:
            if re.match(regex, return_value['data'][i]['fields'][1]['name']):
                # Find all series pass the regex
                series.append(return_value['data'][i])
    if len(series) == 0:
        pass
    else:
        if "datapoints" in series[0]:
            #Hard code for elastic search datasource
            for serie in series:
                time_list = []
                value_list = []
                for p in serie['datapoints']:
                    time_list.append(p[1])
                    value_list.append(p[0])
                algo = None
                if method == 'tsdecomposition':
                    algo = tsdecomposition.TSDecomposition(config, [time_list, value_list])
                elif method == 'holtwinter':
                    algo = holtwinter.HoltWinter(config, [time_list, value_list])
                else:
                    algo = tsdecomposition.TSDecomposition(config, [time_list, value_list])
                if algo is not None:
                    ret = algo.detect()
                    if len(ret['anomaly']) == 0:
                        pass
                    else:
                        # Add anomaly to result
                        copydata = deepcopy(serie)
                        revert_data = [[y, x] for x, y in ret['anomaly'].items()]
                        copydata['datapoints'] = revert_data
                        copydata['target'] += '-anomaly'
                        if isinstance(copydata, dict):
                            # The series in Influxdb is a dict
                            return_value['data'] += [copydata]
                        elif isinstance(copydata, list):
                            # Another series is a list
                            return_value['data'] += copydata
                        else:
                            # Does not support other type
                            pass
                    if len(ret) == 1:
                        # Don't have bound
                        pass
                    else:
                        # Have bound
                        pass
                    
        else:
            for serie in series:
                algo = None
                if method == 'tsdecomposition':
                    algo = tsdecomposition.TSDecomposition(config, [serie['fields'][0]['values'], serie['fields'][1]['values']])
                elif method == 'holtwinter':
                    algo = holtwinter.HoltWinter(config, [serie['fields'][0]['values'], serie['fields'][1]['values']])
                else:
                    algo = tsdecomposition.TSDecomposition(config, [serie['fields'][0]['values'], serie['fields'][1]['values']])
                if algo is not None:
                    ret = algo.detect()
                    if len(ret['anomaly']) == 0:
                        pass
                    else:
                        # Add anomaly to result
                        copydata = deepcopy(serie)
                        copydata['fields'][0]['values'] = list(ret['anomaly'].keys())
                        copydata['fields'][1]['values'] = list(ret['anomaly'].values())
                        copydata['fields'][1]['name'] += '-anomaly'
                        if "name" in copydata:
                            copydata["name"] += "-anomaly"
                        if "config" in copydata['fields'][1]:
                            # Hard code name for influxdb
                            if "displayNameFromDS" in copydata['fields'][1]["config"]:
                                copydata['fields'][1]["config"]["displayNameFromDS"] += '-anomaly'
                        if isinstance(copydata, dict):
                            # The series in Influxdb is a dict
                            return_value['data'] += [copydata]
                        elif isinstance(copydata, list):
                            # Another series is a list
                            return_value['data'] += copydata
                        else:
                            # Does not support other type
                            pass
                    if len(ret) == 1:
                        # Don't have bound
                        pass
                    else:
                        # Have bound
                        upper_bound = deepcopy(serie)
                        upper_bound['fields'][0]['values'] = list(ret['upper'].keys())
                        upper_bound['fields'][1]['values'] = list(ret['upper'].values())
                        upper_bound['fields'][1]['name'] += '-upper-bound'
                        if "name" in upper_bound:
                            upper_bound['name'] += '-upper-bound'
                        if "config" in upper_bound['fields'][1]:
                            # Hard code display name for influxdb
                            if "displayNameFromDS" in upper_bound['fields'][1]["config"]:
                                upper_bound['fields'][1]['config']['displayNameFromDS'] += '-upper-bound'
                        lower_bound = deepcopy(serie)
                        lower_bound['fields'][0]['values'] = list(ret['lower'].keys())
                        lower_bound['fields'][1]['values'] = list(ret['lower'].values())
                        lower_bound['fields'][1]['name'] += '-lower-bound'
                        if "name" in lower_bound:
                            lower_bound['name'] += '-lower-bound'
                        if "config" in lower_bound['fields'][1]:
                            # Hard code display name for influxdb
                            if "displayNameFromDS" in lower_bound['fields'][1]["config"]:
                                lower_bound['fields'][1]['config']['displayNameFromDS'] += '-lower-bound'
                        return_value['data'] += [upper_bound, lower_bound]
    return json(return_value)

if __name__ == "__main__":
    app.run(access_log=True)