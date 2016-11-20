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
stock_set = {}

date = datetime.date(2000, 1, 3)
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
        self.change = 0


class Stock_base:
    def __init__(self, symbol, quantity, price):
        self.symbol = symbol
        self.quantity = quantity
        self.last_price = price
        self.earnings = 0

    def __eq__(self, other):
        if self.symbol == other.symbol:
            return True;

    def __hash__(self):
        return self.symbol.__hash__()

@app.route("/")
def index():
    return render_template('page.html', date = date, stock = stocks, watchlist= watchlist)


@app.route('/stocks')
def trade():
    symbol = request.args['symbol']
    quantity = int(request.args['quantity'])
    q = get_quotes(symbol, date, end)
    if is_symbol(symbol):
        s = Stock(symbol, quantity, date, float(q['Open']))
        sb = Stock_base(symbol, quantity, float(q['Open']))
    if request.args['action'] == 'watchlist':
        watchlist.append(s)
    elif request.args['action'] == 'buy':

        if stock_set.get(symbol):
            stock_set[symbol].quantity += quantity
        else:
            stock_set[symbol] = sb

        for i in range(len(stocks)):
            if stocks[i].symbol==s.symbol and stocks[i].purch_date==s.purch_date: #already there for that date
                stocks[i].quantity += s.quantity
                break
        else:
            stocks.append(s)
    elif request.args['action'] == 'sell':
        for i in range(len(stocks)):
            if stocks[i].symbol == s.symbol:
                stocks[i].quantity += s.quantity

    print(stock_set['AAPL'].last_price)

    return render_template('page.html', date=date, stocks=stocks, watchlist= watchlist)


def is_trading_day(date):
    try:
        get_quotes('YHOO', date, end) is not None
        return True
    except:
        return False


def earning():
    for s,y in stock_set.items():
        if is_symbol(s):
            q = get_quotes(y.symbol, date, end)
            diff = q['Open'] - y.last_price
            y.last_price = q['Open']
            y.earnings += diff*y.quantity
            print("earnings", y.earnings)

def get_quotes(symbol, start_date, end_date):
    try:
        pdr.DataReader(symbol, 'yahoo', start_date, end_date)
        stock = pdr.DataReader(symbol, 'yahoo', start_date, end_date)
        return stock.ix[start_date.isoformat()]
    except:
        return []

def is_symbol(symbol):
    return len(get_quotes(symbol,date,end)) != 0

@app.route('/advance')
def next_day():
    global  date
    #while not is_trading_day(date):

    date += datetime.timedelta(days= 1)
    while not is_trading_day(date):
        date += datetime.timedelta(days=1)
    earning()
    return render_template('page.html', date=date, stocks=stocks, watchlist=watchlist)

def refresh_stocks():

    pass

def earnings(stock):
    q = get_quotes(stock.symbol, date, end)
    open_price = q['Open']
    
if __name__ == '__main__':
    app.run()
