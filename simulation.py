from ryan_tools import * 
import pandas_datareader as pdr

i = 0


#Three functions needed: buy, sell & get_price
#Pandas Dataframe = Price book

#Buy and sell functions need to return True or False, to explain weather or not they succeeded
# A Testing system needs to take a a signal_generator and test it's success based on the time frame
# Should use candle charts


price_data = pd.DataFrame()



def buy(money):
    price =  get_price()
    amount = int(money/price)
    return price * amount, amount

def sell(position):
    price =  get_price() 
    return price * position, position
    

def noise():
    global i
    global price_data
    global data
    if i == 0:
        price_data = pd.DataFrame(columns = data.columns)


    price_data.loc[i] = data.iloc[i]
    price = data.iloc[i]['Close']
    i = i + 1
    return price

def get_price():
    current = len(price_data) - 1
    return price_data.loc[current, 'Close']


def signal_generator(periods):
    if len(price_data) <= periods:
        return 'wait'
    temp = price_data.tail(periods)
    price = get_price()
    if price >= temp['Close'].mean():
        return 'buy'
    if price <= temp['Close'].mean():
        return 'sell'
    return 'wait'


def test():
    money = 1000
    position = 0
    while len(price_data) < len(data):
        noise()
        signal = signal_generator(3)
        
        if signal == 'buy' and money > 0:
            cash_change, amount = buy(money)
            money = money - cash_change
            position = position + amount

        if signal == 'sell' and position > 0:
            cash_change, amount = sell(position)
            money = money + cash_change
            position = position - amount


    cash_change, amount = sell(position)
    money = money + cash_change
    position = position - amount
    return money, position
