#%%
import pandas as pd
import requests
import numpy as np
from datetime import date
from api_handler import APIBMEHandler

APIBME = APIBMEHandler('IBEX', 'javired22_algo1')
maestro_df = APIBME.get_ticker_master()
data_close,data_high,data_low,data_open,data_vol = APIBME.get_data()
benchmark = APIBME.get_close_data_ticker('benchmark')

#indicador estocastico
def stochastic (high, low, close, periodo1, señal):
    L14 =low.rolling(periodo1).min()
    H14= high.rolling(periodo1).max()
    K = 100*((close-L14)/(H14-L14))
    D = K.rolling(señal).mean()
    return L14, H14, K, D
periodo1= 14
señal= 3
L14, H14, K, D = stochastic (data_high, data_low, data_close, periodo1, señal)

#TenkanSen: media movil entre 7 a 9 periodos
#perceived as the short-term line and it represents the average of the high and the low for the 9-period (9-period high + 9-period low / 2).
#Base line (Kijun-sen) – is the long-term line and it is calculated as the average of the high and low for the 26-period (26-period high + 26-period low / 2)
def ichimoku (ventana1,ventana2,ventana3,ventana4, ventana5, high, low, close):
    chikou = close.shift(periods=ventana4)
    tenkan= pd.DataFrame((high.rolling(ventana2).max()+ low.rolling(ventana2).min())/2)
    kijun = pd.DataFrame((high.rolling(ventana4).max()+ low.rolling(ventana4).min())/2)
    span =pd.DataFrame((tenkan+kijun)/2)
    spanA = pd.DataFrame(span.shift(periods=ventana4))
    spanB_aux = pd.DataFrame((high.rolling(ventana5).max()+low.rolling(ventana5).min())/2)
    spanB= pd.DataFrame(spanB_aux.shift(periods=ventana4))
    return chikou, tenkan, kijun, span, spanA, spanB

ventana1=9
ventana2=18
ventana3=26
ventana4=52
ventana5= 104
chikou, tenkan, kijun, span, spanA, spanB = ichimoku (ventana1, ventana2, ventana3, ventana4, ventana5, data_high, data_low, data_close)

data_close = pd.DataFrame(data_close)
chikou= pd.DataFrame(chikou)
type(chikou)

#tengo que ver que close está encima de la nube (span A y B) y compro si tenkan supera al kijun
positions= pd.DataFrame(index=data_close.index, columns=data_close.columns,data=0)
filtro1= K< 30
filtro3 = (data_close > spanB)
filtro4 = tenkan> kijun
filtro5 = data_close > spanB
filtro6 = chikou > data_close

filtro1v = K>70
filtro2v = data_close< spanA
filtro3v = data_close< spanB
filtro4v = tenkan< kijun
positions [filtro1 & filtro3 & filtro4 ]= 1
positions [filtro1v & filtro2v & filtro3v & filtro4v]= -1
positions.shift(periods=1)

positions[positions==0] = None
positions = positions.ffill()
positions[positions == -1] = 0
positions = positions.ffill()
positions[data_close.isna()] = None
volinver = positions*0.03
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

#para hacer backtesting
#for iday in days:
#    alloc_list = [gen_alloc_data(tickers[i], alloc[i]) for i in np.arange(0,data_close.shape[1]) if alloc[i]!=0]  
#    str_date = iday.strftime('%Y-%m-%d')
#    APIBME.post_alloc(str_date, alloc_list)
#%%
#APIBME.run_backtest()
# %%
#APIBME.delete_allocs()
# %%
