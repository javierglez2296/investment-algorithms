#%%
import pandas as pd
import requests
import matplotlib.pyplot as plt
import itertools
import numpy as np
from datetime import date
from api_handler import APIBMEHandler

APIBME = APIBMEHandler('EUROSTOXX', 'javired22_algo3')
maestro_df = APIBME.get_ticker_master()
data_close,data_high,data_low,data_open,data_vol = APIBME.get_data()
benchmark = APIBME.get_close_data_ticker('benchmark')

def ADX(adxlen,periodo2):

    dmpos = data_high.diff()
    dmneg = -(data_low.diff())  
    d = data_high - data_low
    f = abs(data_high.iloc[1:,:]-data_close.iloc[0:-1,:])
    t = abs(data_close.iloc[0:-1,:]-data_low.iloc[1:,:])
    tro1 = d[(d>=f) & (d>=t)] 
    tro2 = f[(f>=t) & (f>d)] 
    tro3 = t[(t>f)&(t>d)]
    tro4 = tro1.add(tro2, fill_value=0)
    tr = tro4.add(tro3, fill_value=0)    
    def rma (data, periodo2):
        rma = data.ewm(alpha=1/periodo2,adjust= False).mean()
        return rma
       
    truerange = rma(tr,periodo2)
    aux1 = dmpos[(dmpos>dmneg) & (dmpos>0)]
    aux1 = aux1.fillna(0)
    dipos = 100 * rma(aux1,periodo2)/truerange
    aux2 =dmneg[(dmpos<dmneg) & (dmneg>0)]
    aux2 = aux2.fillna(0)
    dineg = 100 * rma(aux2,periodo2)/truerange
    
    sumatorio = dipos+dineg

    aux3=sumatorio
    aux3[sumatorio==0]=1

    adx = 100 * rma(abs(dipos-dineg)/aux3,adxlen)

    return adx,dipos,dineg

def EMA(data,periodo):
    emadf = data.ewm(span=periodo,adjust= False).mean()
    return emadf

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
periodo2=12

def bollinger(periodo):
    std= data_close.rolling(periodo).std()
    mean= data_close.rolling(periodo).mean()
    upper_band= mean+ 2*std
    lower_band= mean- 2*std
    return upper_band, lower_band


periodo=40
upper_band, lower_band = bollinger(periodo)
rsi= rsi(periodo2)
adx14,dipos,dineg = ADX(14,14)
positions = pd.DataFrame(index=data_close.index, columns=data_close.columns,data=0)
filtro1= data_close< lower_band
filtro2 = adx14>30
filtro3 = rsi< 30
#Ahora los filtros de ventas
filtro1v = rsi> 60
filtro2v= data_close>upper_band 

positions[ filtro1 & filtro2 & filtro3] = 1
positions[ filtro1v & filtro2v ] = -1
positions= positions.shift(periods=1)
positions[positions==0] = None
positions = positions.ffill()
positions[positions == -1] = 0
positions = positions.ffill()
positions[data_close.isna()] = None

volinver = positions*0.02
volinver[volinver.isna()] = 0
volinver.tail()

def gen_alloc_data(ticker, alloc):
    return {'ticker': ticker,
            'alloc': alloc}
tickers = data_close.columns
tickers = tickers.to_series()
alloc = volinver.iloc[-1,:].values
hoy = date.today().strftime('%Y-%m-%d')

allocation = [gen_alloc_data(tickers[i], alloc[i]) for i in np.arange(0,data_close.shape[1]) if alloc[i]!=0]
APIBME.post_alloc(hoy,allocation)


