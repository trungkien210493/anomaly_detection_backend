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
        if re.match(regex, return_value['data'][i]['fields'][1]['name']):
            # Find all series pass the regex
            series.append(return_value['data'][i])
    for serie in series:
        algo = None
        if method == 'tsdecomposition':
            logger.info([serie['fields'][0]['values'], serie['fields'][1]['values']])
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
                return_value['data'] += copydata
            if len(ret) == 1:
                # Don't have bound
                pass
            else:
                # Have bound
                upper_bound = deepcopy(serie)
                upper_bound['fields'][0]['values'] = list(ret['upper'].keys())
                upper_bound['fields'][1]['values'] = list(ret['upper'].values())
                upper_bound['fields'][1]['name'] += '-upper-bound'
                lower_bound = deepcopy(serie)
                lower_bound['fields'][0]['values'] = list(ret['lower'].keys())
                lower_bound['fields'][1]['values'] = list(ret['lower'].values())
                lower_bound['fields'][1]['name'] += '-lower-bound'
                return_value['data'] += [upper_bound, lower_bound]
    return json(return_value)

if __name__ == "__main__":
    app.run(access_log=True)