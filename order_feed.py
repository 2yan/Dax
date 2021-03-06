import websocket, json
import threading
import GDAX
from ryan_tools import *
import fuckit
import time
import authenticate
import tzlocal

class OrderBook():

    last = None
    time_difference = None
    client = None
    WS_URL = "wss://ws-feed.gdax.com"
    orders = pd.DataFrame(columns = ['type', 'side', 'price', 'order_id', 'remaining_size', 'product_id', 'sequence', 'time'])
    trades = pd.DataFrame(columns = ['side', 'size', 'price','time'])
    product_id = None
    messages = []
    sequence = None
    ws = None
    checker_kill = False
    def message_checker(self):
        
        while True:
            if self.checker_kill == True:
                return
            last_sequence = None
            
            if self.sequence != None:
                if len(self.messages) > 0:
                    message = json.loads(self.messages.pop(0))
                    sequence = message['sequence']

                    if self.sequence < sequence:
                        self.parse_message(message)
                        if last_sequence == None:
                            last_sequence = sequence - 1

                        if last_sequence != sequence -1:
                            print('Issue in Sequence, Resetting Orderbook')
                            self.set_orderbook()
                            last_sequence = None
                            
                        last_sequence = sequence

                        
    def on_message(self,ws, message):
        self.messages.append(message)


        
    def parse_message(self, data):
        
        with fuckit:
            for column in ['price', 'remaining_size', 'size']:
                data[column] = pd.to_numeric(data[column])

            if data['type'] == 'done':
                iden = data['order_id']
                length = len(self.orders)
                self.orders.drop(self.orders.index[self.orders.index == iden], inplace = True )

            if data['type'] == 'open':
                iden = data['order_id']
                data['time'] = pd.to_datetime(data['time']) + self.time_difference
                self.orders.loc[iden] = data

            if data['type'] == 'change':
                iden = data['order_id']
                if iden in self.orders.index:
                    new_size = data['new_size']
                    side = data['side']
                    self.orders.loc[iden, 'remaining_size'] = new_size
                    self.orders.loc[iden, 'side'] = side
                
        if data['type'] == 'match':
            maker_id = data['maker_order_id']
            #taker_id = data['taker_order_id']
            self.last = float(data['price'])
            self.trades.loc[maker_id, 'side'] = data['side']
            self.trades.loc[maker_id, 'size'] = float(data['size'])
            self.trades.loc[maker_id, 'price'] = float(data['price'])
            self.trades.loc[maker_id, 'time'] = datetime.datetime.now()


    
        
    def on_error(self, ws, error):
        print (error)

            
            
    def on_close(self, ws):
        print ("### closed ###")
        self.checker_kill = True
        threading.Thread(target = self.stream_data).start()
        threading.Thread(target = self.set_order_book ).start()
    def on_open(self, ws):
        
        sub = authenticate.get_sub(self.product_id)

        print ("Subscribing to feed...")
        ws.send(json.dumps(sub))

        
    def stream_data(self):
        self.ws = websocket.WebSocketApp(self.WS_URL,
                                    on_message = self.on_message,
                                    on_error = self.on_error,
                                    on_close = self.on_close)
        
        self.ws.on_open = self.on_open
        self.ws.run_forever(http_proxy_host = '127.0.0.1', http_proxy_port= '3120')

        
    def set_order_book(self):
        print('calculating time_difference')
        self.time_difference = pd.to_datetime(self.client.getTime()['iso']) -   datetime.datetime.fromtimestamp(self.client.getTime()['epoch'])
        print('Time Difference ', self.time_difference)
        
        print('waiting for orderbook to download')
        while len(self.messages) == 0:
            time.sleep(0.3)
            print('.', end = '')
        self.sequence = None
        order_book = self.client.getProductOrderBook(level = 3, product = self.product_id)
        
        buy = pd.DataFrame(order_book['bids'], columns  = ['price','remaining_size', 'order_id'])
        buy['side'] = 'buy'
        buy['type'] = 'open'
        buy['product_id'] = self.product_id
        
        sell = pd.DataFrame(order_book['asks'], columns  = ['price','remaining_size', 'order_id'])
        sell['side'] = 'sell'
        sell['type'] = 'open'
        sell['product_id'] = self.product_id
        total = buy.append(sell, ignore_index = True)
        total['sequence'] = self.sequence
        total.index = total['order_id']
        total['time'] = datetime.datetime.now()
        self.orders = self.orders.append(total)
        self.orders['price'] = pd.to_numeric(self.orders['price'])
        
        self.trades['price'] = pd.to_numeric(self.trades['price'])
        self.trades['size'] = pd.to_numeric(self.trades['price'])
        
        self.sequence = int(order_book['sequence'])
        print('OrderBook Downloaded')

        
    def get_spread(self):
        spread = self.client.getProductOrderBook(level = 1, product = 'ETH-USD')
        bids = float(spread['bids'][0][0])
        asks = float(spread['asks'][0][0])
        return bids, asks
        orders = self.orders.copy()
        buy = orders[orders['side'] == 'buy']
        sell = orders[orders['side']== 'sell']
        return buy['price'].max() , sell['price'].min()
    
    def __login(self, product_id):
        config = pd.read_csv('config.csv', index_col = 'iden')
        key = config.loc['key', 'vals']
        secret = config.loc['secret', 'vals']
        passphrase = config.loc['passphrase', 'vals']
        authClient = GDAX.AuthenticatedClient(key, secret, passphrase)
        return authClient
        
    def start(self):
        self.client = self.__login(product_id = self.product_id)
        threading.Thread(target = self.stream_data).start()
        threading.Thread(target = self.message_checker ).start()
        threading.Thread(target = self.set_order_book ).start()



    def __init__(self, product_id = 'ETH-USD' ):
        self.product_id = product_id
        self.start()
            



#-----------------------------------------------------------------------------------------------
def last_minute():
    now = datetime.datetime.now()
    end_time = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute - 1 )
    start_time = end_time - relativedelta(minutes = 200)
    
    return download_candles(start_time, end_time, 200)

    
def download_candles(start_time, end_time, amount):
    if amount > 200:
        raise ValueError('amount Can not be greater than 200')
    if start_time > end_time:
        temp = start_time
        start_time = end_time
        end_time = temp
        del temp
        
    zone = tzlocal.get_localzone()
    client = book.client
    end_time = zone.localize(end_time)
    start_time = zone.localize(start_time)
    granularity = (end_time - start_time).total_seconds()/amount  
    columns = ['time', 'low', 'high', 'open', 'close', 'volume']
    data = pd.DataFrame(data =  client.getProductHistoricRates('',  client.productId, start_time.isoformat(), end_time.isoformat(), granularity ), columns = columns)
    data['time'] = data['time'].apply(datetime.datetime.fromtimestamp)
    return data
    

class Abathur():
    book = None

    def __init__(self, orderbook = None,product_id = 'ETH-USD'):
        if orderbook == None:
            orderbook = OrderBook(product_id)
        self.book = orderbook


    def support_resistance(self, remove_fakes = 0.995, cutoff = 0.95):
        orders = self.book.orders.copy()
        orders['remaining_size'] = pd.to_numeric(orders['remaining_size'])
        if remove_fakes != None:
            orders = orders[orders['remaining_size'] <= orders['remaining_size'].quantile(remove_fakes)]
    
        orders['price'] = orders['price'].apply(int)
        buy = orders[orders['side'] == 'buy'].groupby('price')['remaining_size'].sum()
        sell = orders[orders['side'] == 'sell'].groupby('price')['remaining_size'].sum()

        buy = buy[buy >= buy.quantile(cutoff)]
        sell = sell[sell >= sell.quantile(cutoff)]

        buy = pd.DataFrame(buy)
        sell = pd.DataFrame(sell)
        buy['side'] = 'buy'
        sell['side'] = 'sell'
        
        return buy.append(sell)
    
    def chart_sr(self, data = None):
        if type(data) == type(None):
            data = self.support_resistance(cutoff = 0.00)
        lower = self.book.last * 0.93
        upper = self.book.last * 1.07
        data = data.loc[lower:upper]
        return sea.categorical.barplot(data.index, data['remaining_size'])
        
    def nearest_sr(self, data = None):
        'data = can be custom from  support_resistance()'
        if type(data) == type(None):
            data = self.support_resistance(remove_fakes = 0.995, cutoff = 0.95)

        sell =data[data['side'] == 'sell']
        buy = data[data['side'] == 'buy']
            
        resistance = sell.index.min()
        support = buy.index.max()
        
        return {'support': (support,buy.loc[support,'remaining_size'] ), 'resistance':(resistance, sell.loc[resistance,'remaining_size'])}

    


'''
while True:
    if abathur.book.last != None:
        if last != abathur.book.last:
            print(abathur.nearest_sr() )
            print(abathur.book.last)
            print('.................')
            last = abathur.book.last

'''	
