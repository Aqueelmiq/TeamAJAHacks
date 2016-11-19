from flask import Flask, request, render_template
from random import choice
import os
import urllib.request, urllib.parse, urllib.error, json
import datetime

app = Flask(__name__)


@app.route('/')
def hello_world():
    name = request.args['Enter your name: ']
    return 'Hello Loser!'


if __name__ == '__main__':
    app.run()
