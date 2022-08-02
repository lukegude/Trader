import ccxt
import time


class PaperTrader():
    """
    PaperTrader is a simple trading bot that trades on the paper trading platform.\n\tparameters:\n\t\texchange: the exchange to trade on - default: BinanceUS\n\t\tamount: the amount of the symbol to trade
    """

    def __init__(self, balance=84.67, exchange=None):
        self.exchange = exchange if exchange else ccxt.binanceus()
        self.wallet = {'BTC': 0, 'USD': balance}

    def getBTCPrice(self):
        """
        Get the current price of BTC in USD.
        """
        return self.exchange.fetch_ticker('BTC/USD')['last'] 

    def buy(self,price):
        """
        Buy the specified amount of the symbol at the specified price.\n\tparameters:\n\t\tprice: the price to buy at
        """
        self.wallet['BTC'] += self.wallet['USD'] / price
        self.wallet['USD'] = 0

    def sell(self,price):
        """
        Sell the specified amount of the symbol at the specified price.\n\tparameters:\n\t\tprice: the price to sell at
        """
        self.wallet['USD'] += self.wallet['BTC'] * price
        self.wallet['BTC'] = 0

    def buyOCO(self,price):
        """
        Buy the specified amount of the symbol at the specified price.\n\tparameters:\n\t\tprice: the price to buy at\n\t\tstoploss: the price to sell at if the price goes down
        """
        print('Buying at ' + str(price), 'Stoploss at ' + str(price / 1.002), 'Take Profit at ' + str(price * 1.005))
        self.wallet['BTC'] += self.wallet['USD'] / price
        self.wallet['USD'] = 0


p = PaperTrader()
p.buyOCO(p.getBTCPrice())
print(p.wallet)
