from exchanges.exchange import Exchange
import ccxt


class BinanceAPI(Exchange):
    def __init__(self, exchange=None):
        super().__init__(exchange)
        self.exchange = exchange if exchange else ccxt.binanceus()
        self.exchange.apiKey = self.api
        self.exchange.load_markets()
        self.exchange.secret = self.secret_api
        self.wallet = {'BTC': self.getBTCWallet(), 'USD': self.getUSDWallet()}

    def getBTCWallet(self):
        return self.exchange.fetch_balance()['BTC']['free']

    def getUSDWallet(self):
        return self.exchange.fetch_balance()['USD']['free']


params = {
    'stopLoss': {
        'type': 'limit',  # or 'market'
        'price': 100.33,
        'stopLossPrice': 101.25,
    },
    'takeProfit': {
        'type': 'market',
        'takeProfitPrice': 150.75,
    }
}


# Add datetime to json
def add_datetime(json):
    json['datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return json
