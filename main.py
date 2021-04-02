import pandas as pd
import mplfinance as mpf
import datetime
import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode
import requests

def getTickerByKRName(krName):
    url = "https://api.upbit.com/v1/market/all"
    querystring = {"isDetails":"false"}
    response = requests.request("GET", url, params=querystring)
    market = response.json()
    pair = ''
    for i in market:
        if i['korean_name'] == krName:
            if 'KRW' in i['market'] :
                pair = i['market']
    return pair

def getCandleDataFrame(pair, candleTime, candleLength):
    #candle time은 분 단위. 가능한 값 : 1, 3, 5, 15, 10, 30, 60, 240 로 되어있음.
    url = "https://api.upbit.com/v1/candles/minutes/" + str(candleTime)
    querystring = {"market":pair,"count":candleLength}
    response = requests.request("GET", url, params=querystring)
    minutes = response.json()
    enjin_df = pd.DataFrame(columns=['Open','High','Low','Close','Volume'])
    for idx in reversed(minutes):
        enjin_df.loc[datetime.datetime.strptime(idx['candle_date_time_kst'],'%Y-%m-%dT%H:%M:%S')] = [idx['opening_price'],idx['high_price'],idx['low_price'],idx['trade_price'],idx['candle_acc_trade_volume']]
    return enjin_df

def orderCoin(pair,side,volume,price,ord_type):
    #side   (필수)- bid : 매수- ask : 매도
    #ord_type (필수) - limit : 지정가 주문 - price : 시장가 주문(매수) - market : 시장가 주문(매도)
    access_key = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
    secret_key = os.environ['UPBIT_OPEN_API_SECRET_KEY']

    query = {
        'market': pair,
        'side': side,
        'volume': volume,
        'price': price,
        'ord_type': ord_type,
    }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.post('https://api.upbit.com/v1/orders', params=query, headers=headers)
    return res

if __name__ == '__main__':
    ticker = getTickerByKRName('엔진코인')
    mpf.plot(getCandleDataFrame(ticker, 3, 100),type='candle',mav=5,volume=True)
    result = orderCoin(ticker,'ask',2,4000,'limit')

# mav5 = []
#
# for i in range(len(enjin_df)):
#     if i < 4 :
#         mav5.append(0)
#     else:
#         mav5.append((enjin_df.iloc[i-4]['Close']+enjin_df.iloc[i-3]['Close']+enjin_df.iloc[i-2]['Close']+enjin_df.iloc[i-1]['Close']+enjin_df.iloc[i]['Close']) / 5)
#https://github.com/matplotlib/mplfinance/blob/master/examples/addplot.ipynb
#https://github.com/matplotlib/mplfinance
#
# access_key = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
# secret_key = os.environ['UPBIT_OPEN_API_SECRET_KEY']
#
#
# query = {
#     'state': 'done',
# }
# query_string = urlencode(query).encode()
#
# m = hashlib.sha512()
# m.update(query_string)
# query_hash = m.hexdigest()
#
# payload = {
#     'access_key': access_key,
#     'nonce': str(uuid.uuid4()),
#     'query_hash': query_hash,
#     'query_hash_alg': 'SHA512',
# }
#
# jwt_token = jwt.encode(payload, secret_key)
# authorize_token = 'Bearer {}'.format(jwt_token)
# headers = {"Authorization": authorize_token}
#
# res = requests.get('https://api.upbit.com' + "/v1/orders", params=query, headers=headers)
# print(res.json())