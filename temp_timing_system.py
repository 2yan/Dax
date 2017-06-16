import websocket, json
import threading
import GDAX
from ryan_tools import *
import fuckit
import time
import authenticate
import tzlocal

def one_minute():
    print('one Minute')

def one_hour():
    print('one Hour')

def twenty_seconds():
    print('Twenty Seconds')


def main():
    while True:
        time = datetime.datetime.now()
        if time.second == 0:
            one_minute()
        if time.second%20 == 0:
            twenty_seconds()
        if time.minute == 0:
            one_hour()


