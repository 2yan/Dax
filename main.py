<<<<<<< HEAD
import GDAX
from ryan_tools import *
import threading
import time
import pickle
import random
import order_feed

product_id = 'ETH-USD'
book = order_feed.OrderBook()
book.start()




def login():
    config = pd.read_csv('config.csv', index_col = 'iden')
    key = config.loc['key', 'vals']
    secret = config.loc['secret', 'vals']
    passphrase = config.loc['passphrase', 'vals']
    authClient = GDAX.AuthenticatedClient(key, secret, passphrase)
    return authClient



def account_vals(string = False):
    amount = pd.DataFrame(client.getAccounts())
    amount.index = amount['currency']
    if not string:
        for thing in['available','balance', 'hold']:
            amount[thing] = pd.to_numeric(amount[thing])
    return amount


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


def load():
    global orders
    orders = pickle.load(open('orders.data', 'rb'))
    orders['price'] = pd.to_numeric(orders['price'])
    orders['amount'] = pd.to_numeric(orders['amount'])
def save():
    global orders
    pickle.dump(orders, open('orders.data', 'wb'))

orders = pd.DataFrame(columns = ['amount', 'price'])



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
            
def buy_cheap(seconds, amount):
            
    while True:
        global orders
        old_bid, old_ask = get_price()
        print(old_bid, old_ask)
        for num in range(0, seconds):
            time.sleep(1)
            print('.', end = '' )
        bid, ask = get_price()
        print('timeframe:',seconds,' ', bid, ask, '-----------', sum(orders['amount'] * orders['price'])/orders['amount'].sum() )
        if ask < old_bid:
            x = round(amount, 6)
            result = b(bid + 0.01, x)
            if result != None:
                pos = len(orders)
                orders.loc[pos, 'amount'] = float(x)
                orders.loc[pos, 'price'] = float(result)
                save()
        if account_vals().loc['USD','balance'] <= (amount * float(ask)):
            return 'Done'
        
client = login()
load()

def in_the_money(orders):
    bid, ask = get_price()
    return orders.loc[orders['price'] < bid]

def trade_data(seconds):
    match = book.match.copy()
    start = match.time.max() - relativedelta(seconds = seconds)
    minimum = match.time.min()
    if minimum >= start:
        return 'Wait!'
    data = match[match.time >= start]
    return data
    
def test(time):
    etherium = 0
    usd = 7
    def sell(etherium, usd):
        print('sell')
        result = s( get_price()[0], etherium )
        if result != None:
            usd = result * etherium
            etherium = 0

        return etherium, usd
    
    def buy(etherium = etherium, usd = usd):
        print('buy')
        size = usd/get_price()[1]
        result = b( get_price()[1], size )
        if result != None:
            etherium = usd/result
            usd = 0
        return etherium, usd
    last = 0
    while True:
        data = trade_data(time)
        if type(data) != type(str):
            mean = trade_data(time)['price'].mean()
            if get_price()[0] >= mean and etherium > 0:
                etherium, usd = sell(etherium, usd)
                print('eth:', etherium, '  usd', usd)
            if get_price()[1] <= mean and usd > 0:
                etherium, usd = buy(etherium, usd)
                print('eth:', etherium, '  usd', usd)
            if book.get_price() != last:
                print(book.get_price())
                last = book.get_price()
=======
import GDAX
from ryan_tools import *
import threading
import time
import pickle
import random
import order_feed

product_id = 'ETH-USD'
order_book = order_feed.OrderBook()
order_book.start()




def login():
    config = pd.read_csv('config.csv', index_col = 'iden')
    key = config.loc['key', 'vals']
    secret = config.loc['secret', 'vals']
    passphrase = config.loc['passphrase', 'vals']
    authClient = GDAX.AuthenticatedClient(key, secret, passphrase)
    return authClient



def account_vals(string = False):
    amount = pd.DataFrame(client.getAccounts())
    amount.index = amount['currency']
    if not string:
        for thing in['available','balance', 'hold']:
            amount[thing] = pd.to_numeric(amount[thing])
    return amount


def get_price( product = product_id ):
    return order_book.get_spread()

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
        if kind == 'sell':
            status = client.sell(paramaters)
            paramaters['price'] = get_price()[0] + 0.01
        if 'reject_reason' not in status.keys():
            done = True
            return status
        print(status)


def load():
    global orders
    orders = pickle.load(open('orders.data', 'rb'))
    orders['price'] = pd.to_numeric(orders['price'])
    orders['amount'] = pd.to_numeric(orders['amount'])
def save():
    global orders
    pickle.dump(orders, open('orders.data', 'wb'))

orders = pd.DataFrame(columns = ['amount', 'price'])



def buy_able_amount(dollars):
    price = order_book.get_spread()[1]
    return round(dollars/price,7)

def b(ask, amount):
        print('Trying to buy at', ask )
        start_time = datetime.datetime.now()
        done = False
        order = None
        last_status = None
        while not done:
            if order == None:   
                order = place_order(ask, amount, 'buy')
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
            if (current_time - start_time).seconds >= 60 and order != None:
                print('cancelling')
                print(client.cancelOrder(order['id']))
                return None
            
def s(bid, amount):
        print('Trying to sell at', bid )
        start_time = datetime.datetime.now()
        done = False
        order = None
        last_status = None

        while not done:
            if order == None:   
                order = place_order(bid, amount, 'sell')
            if order != None:
                print('.', end = '')
                status = client.getOrder(order['id'])['status']
                if last_status != status:
                    print(status)
                    last_status = status
                if status == 'done':
                    cost = float(client.getOrder(order['id'])['price'])
                    print('Sold at ', cost )
                    return cost
            current_time = datetime.datetime.now()
            if (current_time - start_time).seconds >= 60 and order != None:
                print('cancelling')
                print(client.cancelOrder(order['id']))
                return None
            
def buy_cheap(seconds, amount):
            
    while True:
        global orders
        old_bid, old_ask = get_price()
        print(old_bid, old_ask)
        for num in range(0, seconds):
            time.sleep(1)
            print('.', end = '' )
        bid, ask = get_price()
        print('timeframe:',seconds,' ', bid, ask, '-----------', sum(orders['amount'] * orders['price'])/orders['amount'].sum() )
        if ask < old_bid:
            x = round(amount, 6)
            result = b(bid + 0.01, x)
            if result != None:
                pos = len(orders)
                orders.loc[pos, 'amount'] = float(x)
                orders.loc[pos, 'price'] = float(result)
                save()
        if account_vals().loc['USD','balance'] <= (amount * float(ask)):
            return 'Done'
        
client = login()
load()

def in_the_money(orders):
    bid, ask = get_price()
    return orders.loc[orders['price'] < bid]
    
>>>>>>> 0ed79a8ffae129fe7553419d46f73575be9b544f
