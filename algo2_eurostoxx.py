#%%
import pandas as pd
import requests
import matplotlib.pyplot as plt
import numpy as np
from datetime import date
from api_handler import APIBMEHandler

APIBME = APIBMEHandler('EUROSTOXX', 'javired22_algo2')
maestro_df = APIBME.get_ticker_master()
data_close,data_high,data_low,data_open,data_vol = APIBME.get_data()
benchmark = APIBME.get_close_data_ticker('benchmark')

def bollinger(periodo):
    std= data_close.rolling(periodo).std()
    mean= data_close.rolling(periodo).mean()
    upper_band= mean+ 2*std
    lower_band= mean- 2*std
    return upper_band, lower_band

def rsi(periodo2):
    delta= pd.DataFrame(data_close.diff())
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0

    gain = pd.DataFrame(up.ewm(com=(periodo2 - 1), min_periods=periodo2).mean())
    loss = pd.DataFrame(down.abs().ewm(com=(periodo2 - 1), min_periods=periodo2).mean())

    RS = pd.DataFrame(gain / loss)
    rsi= pd.DataFrame(100 - (100 / (1 + RS)))
    return rsi

periodo= 50
periodo2=12
rsi= rsi(periodo2)
upper_band, lower_band = bollinger(periodo)

filtro1= rsi<30
filtro2= data_close< lower_band
filtro1v = rsi>70
filtro2v = data_close>upper_band
positions= pd.DataFrame(index=data_close.index, columns=data_close.columns,data=0)
positions[filtro1 & filtro2]= 1
positions[filtro1v & filtro2v] = -1

positions[positions==0] = None
positions = positions.ffill()
positions[positions == -1] = 0
positions = positions.ffill()
positions[data_close.isna()] = None

positions= positions.shift(periods=1)
volinver = positions*0.02
volinver[volinver.isna()] = 0

def gen_alloc_data(ticker, alloc):
    return {'ticker': ticker,
            'alloc': alloc}
tickers = data_close.columns
tickers = tickers.to_series()
alloc = volinver.iloc[-1,:].values
hoy = date.today().strftime('%Y-%m-%d')
allocation = [gen_alloc_data(tickers[i], alloc[i]) for i in np.arange(0,data_close.shape[1]) if alloc[i]!=0]  
APIBME.post_alloc(hoy,allocation)