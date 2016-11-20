from flask import Flask, request, render_template
import plotly.plotly as py
from plotly.tools import FigureFactory as FF
from plotly.graph_objs import *
import random
import time
import datetime
import pandas_datareader.data as pdr

app = Flask(__name__)

py.sign_in('AqueelMiqdad', 'vzmcif6vo5')

#Main Stocks library
stocks = []
watchlist = []
stock_set = {}

###DEFAULTS:
date = datetime.date(2000, 1, 3)
end = datetime.date(2016, 11, 11)
money = 100000
game_status = False

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
        self.img = ''


class Stock_base:
    def __init__(self, symbol, quantity, price):
        self.symbol = symbol
        self.quantity = quantity
        self.last_price = price
        self.earnings = 0

    def __eq__(self, other):
        if self.symbol == other.symbol:
            return True

    def __hash__(self):
        return self.symbol.__hash__()

@app.route("/") #asking the user for dates
def index():
    yesterday = (datetime.date.today() - datetime.timedelta(days=1))
    return render_template('index.html', yesterday=yesterday.isoformat()) #needs the day before today


@app.route("/start")
def start():
    global date, end
    s_date = request.args['start_date'].split("-")
    e_date = request.args['end_date'].split("-")
    date = datetime.date(int(s_date[0]),int(s_date[1]),int(s_date[2]))
    end = datetime.date(int(e_date[0]),int(e_date[1]),int(e_date[2]))
    money = int(request.args['money'])
    return render_template('page.html', date = date, end=end, stock = stocks, watchlist= watchlist, stock_set=stock_set.values(), money=money)


@app.route('/stocks')
def trade():
    global money
    symbol = request.args['symbol'].upper()
    quant = request.args['quantity']
    quantity = int(quant) if quant else 0
    q = get_quotes(symbol, date, end)
    if is_symbol(symbol):
        s = Stock(symbol, quantity, date, float(q['Open']))
        sb = Stock_base(symbol, quantity, float(q['Open']))
        if request.args['action'] == 'watchlist':
            for w in watchlist:
                if s.symbol == w.symbol:
                    break
            else: #not in watchlist
                s.img = graph_gen(symbol, date)
                watchlist.append(s)
                watchlist.sort(key=lambda sw: sw.symbol)
        elif request.args['action'] == 'buy':
            money -= quantity*s.init_price
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
            money += quantity * s.init_price
            sb = Stock_base(symbol, 0-quantity, float(q['Open']))
            if stock_set.get(symbol):
                stock_set[symbol].quantity -= quantity
                if stock_set[symbol].quantity == 0:
                    del stock_set[symbol]
            else:
                stock_set[symbol] = sb

            for i in range(len(stocks)):
                if stocks[i].symbol==s.symbol and stocks[i].purch_date==s.purch_date: #already there for that date
                    stocks[i].quantity -= s.quantity
                    break
            else:
                s.quantity = 0 - quantity
                stocks.append(s)

    else: #not a valid symbol (or maybe not a valid date for that symbol)
        pass #print out some error

    return render_template('page.html', date=date, end=end, stocks=stocks, watchlist= watchlist, stock_set=stock_set.values(), money=money)

@app.route("/game")
def game():
    s_date = request.args['start_date'].split("-")
    e_date = request.args['end_date'].split("-")
    money = request.args['start']
    diff = request.args['diff']
    if diff == 'hard':
        target = random.randrange(money*1.3, money*1.5)
        sleep_time = random.randrange(45, 60)
    elif diff == 'medium':
        target = random.randrange(money * 1.15, money * 1.3)
        sleep_time = random.randrange(60, 100)
    else:
        target = random.randrange(money * 1.05, money * 1.15)
        sleep_time = random.randrange(100, 160)
    global game_status

    game_status = True
    flag = True

    while flag:
        while game_status:
            time.sleep(int(sleep_time))
            i = int(random.randrange(1, 4))
            rand_advance(i)
            render_template('page.html', date=date, end=end, stock=stocks, watchlist=watchlist,
                            stock_set=stock_set.values(), money=money)

        if date >= e_date:
            flag = False
            if money > target:
                status = "You Won by " + str(target - money) + " - Amazing!!"
            else:
                status = "You didnt cut it! Practice more. Use simulators"

    return render_template('page.html', date = date, end=end, stock = stocks, watchlist= watchlist, stock_set=stock_set.values(), money=money)


@app.route("/stopgame")
def stop_game():
    global game_status
    game_status = False
    return render_template('page.html', date=date, end=end, stock=stocks, watchlist=watchlist,
                           stock_set=stock_set.values(), money=money)

def is_trading_day(date):
    if len(get_quotes('YHOO', date, end)) != 0:
        return True
    else:
        return False


def earning():
    global money
    for s,y in stock_set.items():
        if is_symbol(s):
            q = get_quotes(y.symbol, date, end)
            diff = q['Open'] - y.last_price
            y.last_price = q['Open']
            y.earnings += diff*y.quantity

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
def advance():
    global  date
    next_date = date
    time_amount = request.args['advance']
    if time_amount == 'Day':
        next_date += datetime.timedelta(days= 1)
    elif time_amount == 'Week':
        next_date += datetime.timedelta(weeks= 1)
    elif time_amount == 'Month':
        next_date += datetime.timedelta(days= 30)
    elif time_amount == 'Year':
        next_date += datetime.timedelta(days= 365)
    elif time_amount == 'Decade':
        next_date += datetime.timedelta(days= 3650)

    if next_date <= end:
        date = next_date

    while not is_trading_day(date):
        date += datetime.timedelta(days=1)
    earning()
    return render_template('page.html', date=date, end=end, stocks=stocks, watchlist=watchlist, stock_set=stock_set.values(), money = money)

def rand_advance(case):
    global  date
    next_date = date
    time_amount = request.args['advance']
    if case == 1:
        next_date += datetime.timedelta(days= 1)
    elif case == 2:
        next_date += datetime.timedelta(weeks= 1)
    else:
        next_date += datetime.timedelta(days= 30)

    if next_date <= end:
        date = next_date

    while not is_trading_day(date):
        date += datetime.timedelta(days=1)
    earning()

def earnings(stock):
    q = get_quotes(stock.symbol, date, end)
    open_price = q['Open']

def graph_gen(symbol, current_date):
    beginning = current_date - datetime.timedelta(days=30)
    df = pdr.DataReader(symbol, 'yahoo', beginning, current_date)
    fig = FF.create_candlestick(df.Open, df.High, df.Low, df.Close, dates=df.index)
    return py.plot(fig, filename=symbol, validate=False)
    
if __name__ == '__main__':
    app.run()
