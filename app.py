from flask import Flask, request, render_template
from random import choice
import os
import urllib.request, urllib.parse, urllib.error, json
import datetime
import pandas_datareader.data as pdr

app = Flask(__name__)

#Main Stocks library
stocks = []
watchlist = []
date = datetime.date(2000, 1, 1)
end = datetime.date(2017, 1, 1)

class Stock:
    def __init__(self, symbol, quantity, purch_date, init_price):
        self.symbol = symbol
        self.quantity = quantity
        self.purch_date = purch_date
        self.init_price = init_price
        self.earnings = 0
        self.last_price = init_price
        self.last_earning = 0

@app.route("/")
def index():
    return render_template('page.html')


@app.route("/advance")
def advance_day():
    global date
    date += datetime.timedelta(days=1)
    while not is_trading_day(date):
        date += datetime.timedelta(days=1)
    update_stocks()
    return render_template('stocks.html', date=date, stocks=stocks)


def update_stocks():
    for s in stocks:
        q = fetch_quotes(s.symbol, date, date)
        if q:
            s.earnings = s.quantity * (float(q['Close']) - s.init_price)
            s.last_earning = s.quantity * (float(q['Close']) - s.last_price)
            s.last_price = float(q['Close'])


@app.route('/stocks')
def trade():
    symbol = request.args['symbol']
    quantity = int(request.args['quantity'])
    q = fetch_quotes(symbol, date, end)
    if q:
        s = Stock(symbol, quantity, date, q)
        stocks.append(s)
    return render_template('stocks.html', date=date, stocks=stocks)


def is_trading_day(date):
    return fetch_quotes('YHOO', date, end) is not None


def fetch_quotes(symbol, start_date, end_date):
    stock = pdr.DataReader(symbol, 'yahoo', start_date, end_date)
    #print(stock)
    print(start_date)
    print(stock.ix['2010-01-04']['Open'])
    return float(stock.ix['2010-01-04']['Open'])



if __name__ == '__main__':
    app.run()
