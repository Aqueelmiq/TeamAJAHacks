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

@app.route("/")
def index():
    return render_template('page.html', date = date, stock = stocks)



@app.route('/stocks')
def trade():
    symbol = request.args['symbol']
    quantity = int(request.args['quantity'])
    if request.args['action'] == 'watchlist':
        if is_symbol(symbol):
            watchlist.append(symbol)
        #might want to tell the user that that is not a symbol
    elif request.args['action'] == 'buy':
        q = get_quotes(symbol, date, end)
        if len(q) != 0:
            s = Stock(symbol, quantity, date, float(q['Open']))
            stocks.append(s)
    return render_template('page.html', date=date, stocks=stocks)


def is_trading_day(date):
    try:
        get_quotes('YHOO', date, end) is not None
        return True
    except:
        return False



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
    return render_template('page.html', date=date, stocks=stocks, watchlist=watchlist)

def refresh_stocks():

    pass


if __name__ == '__main__':
    app.run()
