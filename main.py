import os
from sanic.log import logger
from sanic import Sanic
from sanic.response import HTTPResponse
from sanic.request import Request
from sanic import json
from sanic_ext import Extend
from copy import deepcopy


app = Sanic("AnomalyDetectionApp")
app.config.CORS_ORIGINS = '*'
Extend(app)

@app.get("/api/list")
async def list_handle(request: Request) -> HTTPResponse:
    return json([{"label": "Time Series Decomposition", "value": "tsdecomposition"}, 
                {"label": "Holt-Winter", "value": "holtwinter"},
                {"label": "Minmax", "value": "minmax"}])

@app.post("/api/query")
async def anomaly_handle(request: Request) -> HTTPResponse:
    logger.info("data is:")
    # logger.info(request.body)
    body = request.json
    logger.info(body)
    logger.info("here")
    # # Find min max to do example - Start
    # for i in range(1, len(body['data'])):
    #     min_value = min(body['data'][i]['fields'][1]['values'])
    #     list_min_index = [i for i, v in enumerate(body['data'][i]['fields'][1]['values']) if v == min_value]
    #     body['data'][i]['fields'][1]['values'] = [min_value]*len(list_min_index)
    #     time_values = [body['data'][i]['fields'][0]['values'][index] for index in list_min_index]
    #     body['data'][i]['fields'][0]['values'] = time_values
    # # Find min max to do example - End
    # body['key'] = body['key'].replace('mixed', 'anomaly')
    # body['data'][1]['fields'][1]['name'] = body['data'][i]['fields'][1]['name'] + '-anomaly'
    # body['data'][1]['length'] = len(list_min_index)
    # # body['data'][0]['refId'] = 'D'
    # logger.info(body)
    copydata = deepcopy(body['data'])
    for i in range(len(copydata)):
        min_value = max(copydata[i]['fields'][1]['values'])
        list_min_index = [i for i, v in enumerate(copydata[i]['fields'][1]['values']) if v == min_value]
        copydata[i]['fields'][1]['values'] = [min_value]*len(list_min_index)
        time_values = [copydata[i]['fields'][0]['values'][index] for index in list_min_index]
        copydata[i]['fields'][0]['values'] = time_values
    copydata[0]['fields'][1]['name'] = copydata[0]['fields'][1]['name'] + '-anomaly'
    logger.info(body)
    body['data'] += copydata
    logger.info("here2")
    logger.info(body)
    return json(body)

if __name__ == "__main__":
    app.run(access_log=True)