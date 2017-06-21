import GDAX
from ryan_tools import *
import threading
import time
import pickle
import random
from order_feed import Abathur

product_id = 'ETH-USD'







def account_vals(string = False):
    amount = pd.DataFrame(abathur.book.client.getAccounts())
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
    return abathur.book.get_spread()

def place_order(price, size, kind , order_type = 'limit',  product_id = product_id):
    size = str(round(float(size),2))
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
            status = abathur.book.client.buy(paramaters)
            paramaters['price'] = get_price()[1] - 0.01
            print(paramaters)
            
        if kind == 'sell':
            status = abathur.book.client.sell(paramaters)
            paramaters['price'] = get_price()[0] + 0.01
            
        if 'reject_reason' not in status.keys():
            done = True 
            return status
        print(status)

def buy_able_amount(dollars):
    price = abathur.book.get_spread()[1]
    return round(dollars/price,7) - 0.02

def cancel_all():
    abathur.book.client.cancelAll()
    
def dump():
    etherium = account_vals().loc['ETH', 'balance']

    done = False
    order = None
    last_status = None
    while not done:
        bid = abathur.book.get_spread()[0] + 0.01
        if order == None:   
            order = place_order(bid, etherium, 'sell')
        if order != None:
            print('.', end = '')
            print(order)
            print()
            try :
                status = abathur.book.client.getOrder(order['id'])['status']
            except KeyError:
                print(order)
                return
            if last_status != status:
                print(status)
                last_status = status
            if status == 'done':
                cost = float(abathur.book.client.getOrder(order['id'])['price'])
                print('Sold at ', cost )
                return cost
            if float(order['price']) - bid > 0.03:
                cancel_all()
                order = None

def gobble():
    
    
    done = False
    order = None
    last_status = None
    while not done:
        etherium = buy_able_amount(account_vals().loc['USD', 'balance'])
        ask = abathur.book.get_spread()[1] - 0.01
        if order == None:   
            order = place_order(ask, etherium, 'buy')
        if order != None:
            print('.', end = '')
            print(order)
            print(ask)
            try :
                status = abathur.book.client.getOrder(order['id'])['status']
            except KeyError:
                print(order)
                return
            if last_status != status:
                print(status)
                last_status = status
            if status == 'done':
                cost = float(abathur.book.client.getOrder(order['id'])['price'])
                print('Purchased at', cost )
                return cost
            if ask - float(order['price']) > 0.03:
                cancel_all()
                order = None
                
def hold_line(low_point, high_point):
    current = 'out'
    extra_last = 0
    
    while True:
        now = abathur.book.last
        bid, ask = abathur.book.get_spread()
        if bid > ask:
            abathur.book.ws.close()
        if abathur.book.last < low_point and current == 'in':
            dump()
            current = 'out'
        if abathur.book.last > high_point and current == 'out':
            gobble()
            current = 'in'
        if now != extra_last:
            print(now)
            extra_last = now

def get_stats():
    return client.getProduct24HrStats(product  = 'ETH-USD')

paramaters = {
        'price': 210,
        'size': 5.71,
        'post_only':True,
        'product_id':'ETH-USD',
        'type' : 'limit'
        }
client = login()
abathur = Abathur()
