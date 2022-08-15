from datetime import datetime
from sys import exc_info
from exchanges.binance import BinanceAPI
from PaperTrader import PaperTrader
import joblib
import os
import pandas as pd
import pandas_ta as ta
import time
import json
import ccxt


class Timer():
    def __init__(self):
        self.start = None
        self.time = None

    def start_timer(self):
        self.start = time.time()

    def get_time(self):
        self.time = time.time() - self.start
        return self.time


class Trader:
    def __init__(self, exchange=None):
        self.exchange_api = exchange if exchange else BinanceAPI()
        self.exchange = self.exchange_api.exchange

        self.five_model = joblib.load(
            os.getcwd() + '/models/five_model.joblib')
        self.ten_model = joblib.load(os.getcwd() + '/models/ten_model.joblib')
        self.twenty_model = joblib.load(
            os.getcwd() + '/models/twenty_model.joblib')
        self.thirty_model = joblib.load(
            os.getcwd() + '/models/thirty_model.joblib')

    def get_stop_profit(self, df):
        try:
            profit = ((df['Average'].iloc[-1] / 100) *
                      df['close'].iloc[-1]) + df['close'].iloc[-1]
            stop_loss = min([df['5 Minutes'].iloc[-1], df['10 Minutes'].iloc[-1],
                            df['20 Minutes'].iloc[-1], df['30 Minutes'].iloc[-1]])
            stop_loss = -abs(stop_loss)
            stop_loss = ((stop_loss/100) *
                         df['close'].iloc[-1]/100) + df['close'].iloc[-1]
            return profit, stop_loss
        except KeyError:
            print('ML model not ran')

    def predict_next_close(self, df):
        five_predictions = self.five_model.predict(
            df[['MACD', 'STOCHRSIk', 'STOCHRSId', 'BandWidth']])
        ten_predictions = self.ten_model.predict(
            df[['MACD', 'STOCHRSIk', 'STOCHRSId', 'BandWidth']])
        twenty_predictions = self.twenty_model.predict(
            df[['MACD', 'STOCHRSIk', 'STOCHRSId', 'BandWidth']])
        thirty_predictions = self.thirty_model.predict(
            df[['MACD', 'STOCHRSIk', 'STOCHRSId', 'BandWidth']])
        df['5 Minutes'] = five_predictions
        df['10 Minutes'] = ten_predictions
        df['20 Minutes'] = twenty_predictions
        df['30 Minutes'] = thirty_predictions
        df['Average'] = (df['5 Minutes'] + df['10 Minutes'] +
                         df['20 Minutes'] + df['30 Minutes'])/4
        return df.tail(1)

    def get_data(self, start_date=None, timeframe='5m'):
        data = self.exchange.fetch_ohlcv(
            'BTC/USD', timeframe, limit=1000, since=start_date)
        df = pd.DataFrame(
            data, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['date'], unit='ms')
        df['MACD'] = ta.macd(df['close'], n_fast=12, n_slow=26,
                             n_sign=9)['MACDh_12_26_9']
        df['macd_low'] = ta.macd(df['close'], n_fast=12, n_slow=26,
                                 n_sign=9)['MACD_12_26_9']
        df['macd_high'] = ta.macd(df['close'], n_fast=12, n_slow=26,
                                  n_sign=9)['MACDs_12_26_9']
        df['Trend'] = (df['macd_high'] <= 0) & (df['macd_low'] <= 0)
        df['Trend'] = df['Trend'].map({True: 'Below', False: 'Above'})
        df.drop(['macd_high', 'macd_low'], axis=1, inplace=True)
        df['200EMA'] = ta.ema(df['close'], n=200)
        df['STOCHRSIk'] = ta.stochrsi(df['close'], n=14)['STOCHRSIk_14_14_3_3']
        df['STOCHRSId'] = ta.stochrsi(df['close'], n=14)['STOCHRSId_14_14_3_3']
        df['BandWidth'] = ta.bbands(df['close'], n=20, k=2)['BBB_5_2.0']
        df['BuySignal'] = ((df['close'] > df['200EMA']) & (df['MACD'] >= 1) & (
            df['STOCHRSId'] >= 50) & (df['STOCHRSId'] >= 50))
        df['SellSignal'] = ((df['MACD'] <= 0) & (df['STOCHRSId'] <= 50))
        df.dropna(inplace=True)
        return df

    def log_trade(order):
        with open('orders.json', 'r+') as f:
            orders = json.load(f)
            formatted_data = {"Date": datetime.now().strftime(
                '%Y-%m-%d %H:%M:%S'), "Side": order['side'], "Balance": order['cummulativeQuoteQty']}
            orders['Trades'].append(formatted_data)
            f.seek(0)
            json.dump(orders, f)
            f.truncate()

    def clear_json(self):
        with open('orders.json', 'w') as f:
            json.dump({'Trades': []}, f)
            f.truncate()

    def start(self, paper=False):
        if paper:
            self.exchange_api = PaperTrader()
            self.exchange = ccxt.binanceus()
            print('Loaded PaperTrader')
        self.clear_json()
        while True:
            try:
                df = self.get_data()
                if df['BuySignal'].iloc[-1] == 'Buy' and self.exchange_api.in_position == False:
                    print('Buy Signal')
                    order = self.exchange_api.place_order('BUY')
                    self.log_trade(order)
                elif df['SellSignal'].iloc[-1] == 'Sell' and self.exchange_api.in_position == True:
                    print('Sell Signal')
                    order = self.exchange_api.place_order('SELL')
                    self.log_trade(order)
                else:
                    print('No Signal')
            except Exception as e:
                print(e)
                exit()


if __name__ == '__main__':
    trader = Trader()
    trader.start(True)
