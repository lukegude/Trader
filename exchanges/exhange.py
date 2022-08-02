import os
import ccxt
import json


class Exchange:
    def __init__(self, exchange=None):
        try:
            self.api = self.GET_API_KEY()['API-KEY']
        except Exception as e:
            print(e)
            exit()


    def GET_API_KEY(self):
        with open(os.getcwd() + '/config/config.json') as f:
            keys = json.load(f)
            if not keys['API-KEY']:
                raise Exception('No API-KEY found in config.json')
            return keys


e = Exchange()
print(e.api)
