from flask import Flask, request, render_template
from random import choice
import os
import urllib.request, urllib.parse, urllib.error, json
import datetime
import pandas_datareader.data as pdr

app = Flask(__name__)

#Main Stocks library
stocks = []
watchlist = ['AAPL', 'GOOG', 'MSFT']
date = datetime.date(2000, 1, 1)

aapl = pdr.DataReader("AAPL", 'yahoo', start, end)
print(aapl.ix['2007-06-29'])


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


@app.route('/trade')
def trade():
    symbol = request.args['symbol']
    quantity = int(request.args['quantity'])
    q = fetch_quotes(symbol, date, date)
    if q:
        s = Stock(symbol, quantity, date, float(q['Open']))
        stocks.append(s)
    return render_template('stocks.html', date=date, stocks=stocks)


def is_trading_day(date):
    return fetch_quotes('YHOO', date, date) is not None


def fetch_quotes(symbol, start_date, end_date):
    try:
        stock = pdr.DataReader(symbol, 'yahoo', start_date, end_date)
        if stock:
            return stock['quote']
        else:
            return None
    except urllib.error.HTTPError:
        return None


if __name__ == '__main__':
    app.run()
