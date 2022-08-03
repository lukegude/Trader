from exhange import Exchange
import ccxt
class BinanceAPI(Exchange):
    def __init__(self, exchange=None):
        super().__init__()
        self.exchange = exchange if exchange else ccxt.binanceus()
        self.exchange.apiKey = self.api
        self.exchange.secret = self.secret_api
        self.wallet = {'BTC': self.getBTCWallet(), 'USD': self.getUSDWallet()}

    def getBTCWallet(self):
        return self.exchange.fetch_balance()['BTC']['free']

    def getUSDWallet(self):
        return self.exchange.fetch_balance()['USD']['free']



b = BinanceAPI()
print(b.wallet)