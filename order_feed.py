<<<<<<< HEAD
import websocket, json
import threading
import GDAX
from ryan_tools import *
import fuckit
import logging
import time



    



class OrderBook():
    downloader = None
    ws = None
    WS_URL = "wss://ws-feed.gdax.com"
    orders = pd.DataFrame(columns = ['type', 'side', 'price', 'order_id', 'remaining_size', 'product_id', 'sequence', 'time'])
    match = pd.DataFrame(columns = ['type', 'trade_id', 'maker_order_id', 'taker_order_id', 'side', 'size', 'price', 'product_id', 'sequence', 'time'])
    product_id = 'ETH-USD'
    last = None
    messages = []
            
    def on_message(self, ws, message):
        self.messages.append(message)

    def message_parser(self):
        while True:
            if len(self.messages) > 0:
                message = self.messages.pop(0)
                self.parse_message(message)
        
    def parse_message(self, message):
        first_spread =  self.get_spread()
        data =json.loads(message)

        if self.last != None:
            if self.last + 1 != data['sequence']:
                print('Given Message :',  data['sequence'])
                print('Last Value :', self.last)
                raise ValueError('Sequence NOT OK!')
        self.last = data['sequence']
            
        with fuckit:
            for column in ['price', 'remaining_size', 'size']:
                data[column] = pd.to_numeric(data[column])
                
        if data['type'] == 'open':
            iden = data['order_id']
            self.orders.loc[iden] = data

        if data['type'] == 'match':
            location = data['sequence']
            data['time'] = pd.to_datetime(data['time'])
            self.match.loc[location] = data
 
        if data['type'] == 'done':
            iden = data['order_id']
            self.orders.drop(self.orders.index[self.orders.index == iden], inplace = True )
            
        
            
        if data['type'] == 'change':
            print('Order Changed, Book does not account for this yet')
            print(data)
            print('------------')
            '''
            iden = data['order_id']
            new_size = data['new_size']
            side = data['side']
            self.orders.loc[iden, 'remaining_size'] = new_size
            self.orders.loc[iden, 'side'] = side
            '''
            
    def on_error(self, ws, error):
        print (error)

    def on_close(self, ws):
        print ("### closed ###")

    def on_open(self, ws):
        sub = {
            "type": "subscribe",
            "product_id": self.product_id
        }
        print ("Subscribing to feed...")
        ws.send(json.dumps(sub))

    def _begin(self):
        self.ws = websocket.WebSocketApp(self.WS_URL,
                                    on_message = self.on_message,
                                    on_error = self.on_error,
                                    on_close = self.on_close)
        self.ws.on_open = self.on_open
        
        self.ws.run_forever(http_proxy_host = '127.0.0.1', http_proxy_port= '3120')

    def get_price(self):
        return float(self.match.tail(1)['price'].values[0])

    def start(self):
        public = GDAX.PublicClient()
        self.downloader = threading.Thread(target = self._begin)
        self.downloader.start()
        threading.Thread(target = self.message_parser ).start()
        '''
        order_book = public.getProductOrderBook(level = 3, product = self.product_id)
        sequence = order_book['sequence']
        buy = pd.DataFrame(order_book['bids'], columns  = ['price','remaining_size', 'order_id'])
        buy['side'] = 'buy'
        buy['type'] = 'open'
        buy['product_id'] = self.product_id
        
        sell = pd.DataFrame(order_book['asks'], columns  = ['price','remaining_size', 'order_id'])
        sell['side'] = 'sell'
        sell['type'] = 'open'
        sell['product_id'] = self.product_id

        total = buy.append(sell)
        total['sequence'] = sequence
        total.index = total['order_id']
        self.orders = self.orders[ - (self.orders['sequence'] <= sequence)]
        self.orders = self.orders.append(total)
        '''
        self.orders['price'] = pd.to_numeric(self.orders['price'])
        self.orders['remaining_size'] = pd.to_numeric(self.orders['remaining_size'])
        
    def get_relavent(self):
        buys = self.orders[self.orders['side'] == 'buy']
        price = self.get_price()
        
        buys = buys[buys['price'] >= price - 1]
        
        sells = self.orders[self.orders['side'] == 'sell']
        sells = sells[sells['price'] <= price + 1]
        final = buys.append(sells)
        final['power'] = final['price'] * final['remaining_size']
        final['power'] = pd.to_numeric(final['power'])
        final['price'] = pd.to_numeric(final['price'])
        final['remaining_size'] = pd.to_numeric(final['remaining_size'])
        return final
    
    def get_spread(self):
        orders = self.orders
        while True:
            try:
                return orders[orders['side'] == 'buy'].price.max(), orders[orders['side'] == 'sell'].price.min()
            except:
                pass
            
    def close(self):
        self.ws.close()
    

            

=======
import websocket, json
import threading
import GDAX
from ryan_tools import *
import fuckit
import logging

import time




class OrderBook():
    downloader = None
    ws = None
    WS_URL = "wss://ws-feed.gdax.com"
    orders = pd.DataFrame(columns = ['type', 'side', 'price', 'order_id', 'remaining_size', 'product_id', 'sequence', 'time'])
    match = pd.DataFrame(columns = ['type', 'trade_id', 'maker_order_id', 'taker_order_id', 'side', 'size', 'price', 'product_id', 'sequence', 'time'])
    product_id = 'ETH-USD'
    last = None
    messages = []
    def on_message(self, ws, message):
        self.messages.append(message)

    def message_parser(self):
        while True:
            if len(self.messages) > 0:
                message = self.messages.pop(0)
                self.parse_message(message)
        
        
    def parse_message(self, message):
        
        data =json.loads(message)
        


        with fuckit:
            for column in ['price', 'remaining_size', 'size']:
                data[column] = pd.to_numeric(data[column])
                
        if data['type'] == 'open':
            iden = data['order_id']
            self.orders.loc[iden] = data

        if data['type'] == 'match':
            location = data['sequence']
            self.match.loc[location] = data
 
        if data['type'] == 'done':
            iden = data['order_id']
            self.orders.drop(self.orders.index[self.orders.index == iden], inplace = True )
            return
            
        if data['type'] == 'change':
            print(data)

            
    def on_error(self, ws, error):
        print (error)

    def on_close(self, ws):
        print ("### closed ###")

    def on_open(self, ws):
        sub = {
            "type": "subscribe",
            "product_id": self.product_id
        }
        print ("Subscribing to feed...")
        ws.send(json.dumps(sub))

    def _begin(self):
        self.ws = websocket.WebSocketApp(self.WS_URL,
                                    on_message = self.on_message,
                                    on_error = self.on_error,
                                    on_close = self.on_close)
        self.ws.on_open = self.on_open
        
        self.ws.run_forever(http_proxy_host = '127.0.0.1', http_proxy_port= '3120')

    def get_price(self):
        return float(self.match.tail(1)['price'].values[0])

    def start(self):

        public = GDAX.PublicClient()
        self.downloader = threading.Thread(target = self._begin)
        self.downloader.start()
        threading.Thread(target = self.message_parser ).start()
        order_book = public.getProductOrderBook(level = 3, product = self.product_id)
        sequence = order_book['sequence']
        buy = pd.DataFrame(order_book['bids'], columns  = ['price','remaining_size', 'order_id'])
        buy['side'] = 'buy'
        buy['type'] = 'open'
        buy['product_id'] = self.product_id
        sell = pd.DataFrame(order_book['asks'], columns  = ['price','remaining_size', 'order_id'])
        sell['side'] = 'sell'
        sell['type'] = 'open'
        sell['product_id'] = self.product_id
        total = buy.append(sell)
        total['sequence'] = 0
        total.index = total['order_id']
        self.orders = self.orders[ - (self.orders['sequence'] <= sequence)]
        self.orders = self.orders.append(total)

        self.orders['price'] = pd.to_numeric(self.orders['price'])
        self.orders['remaining_size'] = pd.to_numeric(self.orders['remaining_size'])
        
    def get_relavent(self):
        buys = self.orders[self.orders['side'] == 'buy']
        price = self.get_price()
        
        buys = buys[buys['price'] >= price - 1]
        
        sells = self.orders[self.orders['side'] == 'sell']
        sells = sells[sells['price'] <= price + 1]
        final = buys.append(sells)
        final['power'] = final['price'] * final['remaining_size']
        final['power'] = pd.to_numeric(final['power'])
        final['price'] = pd.to_numeric(final['price'])
        final['remaining_size'] = pd.to_numeric(final['remaining_size'])
        return final
    def get_spread(self):
        orders = self.orders
        while True:
            try:
                return orders[orders['side'] == 'buy'].price.max(), orders[orders['side'] == 'sell'].price.min()
            except:
                pass
    def close(self):
        self.ws.close()
    



def thing():
    last_avg = 0
    last_price = 0
    last_deviation = 0
    while True:
        fif = main.match.tail(50)
        moving_average = fif['price'].mean()
        moving_deviation = (fif['price']/moving_average).std()
        price = main.get_price()
        if (price != last_price) or (last_avg != moving_average) or (moving_deviation != last_deviation) :
            global results
            length = len(results)
            results.loc[length, 'price'] = price
            results.loc[length, 'moving_average'] = moving_average
            results.loc[length, 'std'] = moving_deviation
            
            last_price = price
            last_avg = moving_average
            last_deviation = moving_deviation
            

>>>>>>> 0ed79a8ffae129fe7553419d46f73575be9b544f
