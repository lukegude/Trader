from binance.client import Client
import os
import json
from datetime import datetime


class PaperTrader():
    def __init__(self):
        self.client = Client(self.GET_API_KEYS()[0], self.GET_API_KEYS()[1])
        self.client.API_URL = 'https://testnet.binance.vision/api'
        self.wallet = self.client.get_account()
        self.in_position = False
        self.exchange = 'Binance-Paper'
        self.old_balance = None

    def GET_API_KEYS(self):
        # Open config/personal_config.json
        with open(os.getcwd() + '/config/personal_config.json') as json_file:
            data = json.load(json_file)
            self.api = data['PAPER-API-KEY']
            self.secret_api = data['PAPER-SECRET-KEY']
        return self.api, self.secret_api

    def getWalletBalance(self, ticker='BTC'):
        wallet_index = {'BNB': 0, 'BTC': 1, 'BUSD': 2,
                        'ETH': 3, 'LTC': 4, 'TRX': 5, 'USDT': 6, 'XRP': 7}
        try:
            return float(self.wallet['balances'][wallet_index[ticker]]['free'])
        except KeyError:
            print(f'{ticker} not found in wallet')

    def InPosition(self):
        return self.getWalletBalance('BTC') != 0

    def log_paper_order(self,order):
        with open('orders.json', 'r+') as f:
            orders = json.load(f)
            formatted_data = {"Date": datetime.now().strftime(
                '%Y-%m-%d %H:%M:%S'), "Side": order['side'], "Balance": order['cummulativeQuoteQty'], "BTC": self.getWalletBalance('BTC'), "USD": self.getWalletBalance('USDT')}
            orders['Trades'].append(formatted_data)
            f.seek(0)
            json.dump(orders, f)
            f.truncate()

    def clear_json(self):
        with open('orders.json', 'w') as f:
            json.dump({'Trades': []}, f)
            f.truncate()
    def place_order(self,side):
        if (side.upper() == 'BUY'):
            order = self.client.order_market_buy(
                symbol='BTCUSDT', quoteOrderQty=self.getWalletBalance('USDT'))
            self.in_position = True
        elif (side.upper() == 'SELL'):
            order = self.client.order_market_sell( symbol='BTCUSDT',quantity=self.getWalletBalance('BTC'))
            self.in_position = False
        return order

