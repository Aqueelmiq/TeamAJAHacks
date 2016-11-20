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

@app.route("/") #asking the user for dates
def index():
    yesterday = (datetime.date.today() - datetime.timedelta(days=1))
    return render_template('index.html', today=yesterday.isoformat()) #needs the day before today


@app.route("/start")
def start():
    global date, end
    s_date = request.args['start_date'].split("-")
    e_date = request.args['end_date'].split("-")
    date = datetime.date(int(s_date[0]),int(s_date[1]),int(s_date[2]))
    end = datetime.date(int(e_date[0]),int(e_date[1]),int(e_date[2]))
    return render_template('page.html', date = date, stock = stocks, watchlist= watchlist)


@app.route('/stocks')
def trade():
    symbol = request.args['symbol']
    quant = request.args['quantity']
    quantity = int(quant) if quant else 0
    q = get_quotes(symbol, date, end)
    if is_symbol(symbol):
        s = Stock(symbol, quantity, date, float(q['Open']))
    if request.args['action'] == 'watchlist':
        watchlist.append(s)
    elif request.args['action'] == 'buy':
        for i in range(len(stocks)):
            if stocks[i].symbol==s.symbol and stocks[i].purch_date==s.purch_date: #already there for that date
                stocks[i].quantity += s.quantity
                break
        else:
            stocks.append(s)
    return render_template('page.html', date=date, stocks=stocks, watchlist= watchlist)


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

def earnings(stock):
    q = get_quotes(stock.symbol, date, end)
    open_price = q['Open']
    
if __name__ == '__main__':
    app.run()
