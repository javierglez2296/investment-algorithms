#%%
pip install pytrends --upgrade
# %%
from pytrends.request import TrendReq
import pandas as pd
import time
import numpy as np
import random
from tqdm import tqdm
import investpy
# %%
data_close = pd.DataFrame(data=None, index=None, columns=None, dtype=None, copy=False)
lista_cryptos= ['Bitcoin', 'Ethereum']
i= 0
crypto_list= investpy.crypto.get_cryptos_list()
selected_cryptos= crypto_list[0:50]
#%%
for crypto in tqdm(lista_cryptos):
    df= investpy.crypto.get_crypto_historical_data(crypto, '01/01/2020', '01/04/2021', as_json=False, order='ascending', interval='Daily')
    i= i+1
    data_close[i]= df.iloc[:,3]

# %%
df_interes_cryptos= pd.DataFrame(data=None, index=None, columns=None, dtype=None, copy=False)
trends = {}
i=1
pytrends = TrendReq()
for cryptos in selected_cryptos:
    pytrends.build_payload(kw_list= [cryptos], geo='US', timeframe='2020-01-01 2021-01-01')
    trends[i]= pytrends.interest_over_time()
    i += 1
    time.sleep(1)
df_trends = pd.concat(trends, axis=1)
# %%
df_trends
#%%
data_close.columns= selected_cryptos
# %%
df_interes_cryptos

# %%
correlacion = pd.DataFrame(data=None, index=None, columns=None, dtype=None, copy=False)
for i in range(len(df_interes_cryptos.iloc[:,1])-1):
    correlacion[i]= df_interes_cryptos.iloc[:,i].corr(data_close.iloc[:,i])


# %%
correlacion
# %%
