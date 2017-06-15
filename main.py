import GDAX
from ryan_tools import *
import threading
import time
import pickle
import random
import order_feed
product_id = 'ETH-USD'


def account_vals(string = False):
    amount = pd.DataFrame(client.getAccounts())
    amount.index = amount['currency']
    if not string:
        for thing in['available','balance', 'hold']:
            amount[thing] = pd.to_numeric(amount[thing])
    return amount


def get_usd_values():    
    data = account_vals()
    for index in data.index: 
        amount = data.loc[index, 'balance']
        price = 1
        if index != 'USD':
            price = float(client.getProduct24HrStats(product = index + '-USD')['last'])
        data.loc[index, 'value'] = price * amount
    return data
def dollar_amount():
    return get_usd_values()['value'].sum()

def login():
    config = pd.read_csv('config.csv', index_col = 'iden')
    key = config.loc['key', 'vals']
    secret = config.loc['secret', 'vals']
    passphrase = config.loc['passphrase', 'vals']
    authClient = GDAX.AuthenticatedClient(key, secret, passphrase)
    return authClient




def get_price( product = product_id ):
    return book.get_spread()

def place_order(price, size, kind , order_type = 'limit',  product_id = product_id):
    paramaters = {
        'price': price,
        'size': size,
        'post_only':True,
        'product_id':product_id,
        'type' : order_type
        }
    done = False
    while not done:
        paramaters['price'] = str(round(float(paramaters['price']), 2))
        if kind == 'buy':
            status = client.buy(paramaters)
            paramaters['price'] = get_price()[1] - 0.01
            print(paramaters)
            
        if kind == 'sell':
            status = client.sell(paramaters)
            paramaters['price'] = get_price()[0] + 0.01
            
        if 'reject_reason' not in status.keys():
            done = True 
            return status
        print(status)

def buy_able_amount(dollars):
    price = book.get_spread()[1]
    return round(dollars/price,7)


def b(bid, amount, wait = 60):
        amount = round(amount, 7)
        print('Trying to buy at', bid )
        start_time = datetime.datetime.now()
        done = False
        order = None
        last_status = None
        while not done:
            if order == None:   
                order = place_order(bid, amount, 'buy')
            if order != None:
                print('.', end = '')
                try :
                    status = client.getOrder(order['id'])['status']
                except KeyError:
                    print(order)
                    return
                if last_status != status:
                    print(status)
                    last_status = status

                if status == 'done':
                    cost = float(client.getOrder(order['id'])['price'])
                    print('Purchased at ', cost )
                    return cost
            current_time = datetime.datetime.now()
            if (current_time - start_time).seconds >= wait and order != None:
                print('cancelling')
                print(client.cancelOrder(order['id']))
                return None
            
def s(ask, amount, wait = 60):
        amount = round(amount, 7)
        print('Trying to sell at', ask )
        start_time = datetime.datetime.now()
        done = False
        order = None
        last_status = None

        while not done:
            if order == None:   
                order = place_order(ask, amount, 'sell')
            if order != None:
                print('.', end = '')
                try :
                    status = client.getOrder(order['id'])['status']
                except KeyError:
                    print(order)
                    return
                if last_status != status:
                    print(status)
                    last_status = status
                if status == 'done':
                    cost = float(client.getOrder(order['id'])['price'])
                    print('Sold at ', cost )
                    return cost
            current_time = datetime.datetime.now()
            if ((current_time - start_time).seconds >= wait) and order != None:
                print('cancelling')
                print(client.cancelOrder(order['id']))
                return None

book =  None
client = None

def start(start_book = False):
    global book
    global client
    if start_book:
        book = order_feed.OrderBook()
        book.start()
    client = login()


