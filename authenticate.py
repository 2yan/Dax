import json, hmac, hashlib, time, requests, base64
from requests.auth import AuthBase
from ryan_tools import *

    
    


def get_sub(product_id):
    try:
        config = pd.read_csv('config.csv', index_col = 'iden')
    except FileNotFoundError:
        print('NO config.csv file found, subscribing to unauthenticated feed')
        return {
        "type": "subscribe",
        "product_id": product_id,
        }
    key = config.loc['key', 'vals']
    secret = config.loc['secret', 'vals']
    passphrase = config.loc['passphrase', 'vals']
    
    timestamp = str(time.time())
    message = timestamp + 'SUBSCRIBE' + 'https://api.gdax.com/users/self'
    message = message.encode('ascii')
    hmac_key = base64.b64decode(secret)
    signature = hmac.new(hmac_key, message, hashlib.sha256)
    signature_b64 = base64.b64encode(signature.digest())

    sub = {
        "type": "subscribe",
        "product_id": product_id,
        #'CB-ACCESS-SIGN': signature_b64.decode("utf-8") ,
        #'CB-ACCESS-KEY': key,
        #'CB-ACCESS-PASSPHRASE': passphrase,
        #'CB-ACCESS-TIMESTAMP': timestamp
        
    }

    return sub
        
