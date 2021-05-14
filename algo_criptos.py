
#%%
import pandas as pd
import time
import numpy as np
import random
from tqdm import tqdm
import investpy
#%%
#Getting data of the cryptos
data_open = pd.DataFrame(data=None, index=None, columns=None, dtype=None, copy=False)
data_high = pd.DataFrame(data=None, index=None, columns=None, dtype=None, copy=False)
data_low = pd.DataFrame(data=None, index=None, columns=None, dtype=None, copy=False)
data_close = pd.DataFrame(data=None, index=None, columns=None, dtype=None, copy=False)
data_vol = pd.DataFrame(data=None, index=None, columns=None, dtype=None, copy=False)

lista_cryptos= ['Binance Coin', 'Polkadot', 'Uniswap', 'Solana','Dent','Tron', 'Bittorrent', 'Bitcoin', 'Ethereum', 'Tether', 'Cardano', 'Litecoin', 'AxieInfinity']
i= 0
crypto_list= investpy.crypto.get_cryptos_list()
crypto_list
#%%
selected_cryptos= crypto_list[0:50]
for crypto in tqdm(selected_cryptos):
    df= investpy.crypto.get_crypto_historical_data(crypto, '01/01/2020', '01/04/2021', as_json=False, order='ascending', interval='Daily')
    i= i+1
    data_close[i]= df.iloc[:,3]
    data_open[i]= df.iloc[:,0]
    data_high[i]= df.iloc[:,1]
    data_low[i]= df.iloc[:,2]
    data_vol[i]= df.iloc[:,4]
   
# %%
data_open.columns=selected_cryptos
data_high.columns=selected_cryptos
data_low.columns=selected_cryptos
data_close.columns= selected_cryptos
data_vol.columns= selected_cryptos
# %%
data_close
#%%
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


periodo=20
upper_band, lower_band = bollinger(periodo)
rsi= rsi(periodo2)
adx14,dipos,dineg = ADX(14,14)
positions = pd.DataFrame(index=data_close.index, columns=data_close.columns,data=0)
filtro1= data_close< lower_band
filtro2 = adx14>30
filtro3 = rsi< 40
#Ahora los filtros de ventas
filtro1v = rsi> 60
filtro2v= data_close>upper_band 
#%%
positions[ filtro1 & filtro2 & filtro3] = 1
positions[ filtro1v & filtro2v ] = -1
positions= positions.shift(periods=1)
positions[positions==0] = None
positions = positions.ffill()
positions[positions == -1] = 0
positions = positions.ffill()
positions[data_close.isna()] = None
# %%
positions.to_csv (r'C:\Users\Usuario\Desktop\TFM algortimos\export_dataframe.csv', index = True, header=True, sep='\t', encoding='utf-8')
# %%
situacion_hoy= positions.iloc[-1]
situacion_hoy
#%%
#Comprobar si ha habido compras
for i in range(len(positions.iloc[:,1])):
    for j in range(len(positions.iloc[1,:])):
        if positions.iloc[i,j]==1:
            print('hay compras')
   
# %%
rsi
# %%
investpy.crypto.get_cryptos()
# %%
crypto_list= investpy.crypto.get_cryptos_list()
selected_cryptos= crypto_list[0:50]
# %%
