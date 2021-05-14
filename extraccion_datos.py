#%%
pip install investpy
#%%
import pandas as pd
import time
import numpy as np
import random
from tqdm import tqdm
import investpy

# %%
df = investpy.get_index_historical_data(index='ibex 35',
                                        country='spain',
                                        from_date='01/01/2018',
                                        to_date='01/01/2019')
# %%
import pandas as pd
import numpy as np
import requests
import re
from bs4 import BeautifulSoup
import time
from tqdm import tqdm
# %%
tickers_de_indices=("%5EIBEX")                    
#%%
def componentes_indice(tickers_de_indices):
    """esta funcion devuelve los componentes y divisa de cada indice.
    como parametro se debe inclur los tickers de Yahoo Finance de los indices
    en una tupla"""
    
    n=0

    i=tickers_de_indices
    Index=tickers_de_indices
        
        #primero se obtiene la divisa
    url="https://es.finance.yahoo.com/quote/"+i+"/components/"
    soup  = requests.get(url)
    soup  = BeautifulSoup(soup.content, 'html.parser')
    name_box = soup.find('span', attrs={'data-reactid': '4'})
        
    try:
        name = name_box.text.strip()
        divisa=name[len(name)-3:len(name)]
        print(i,divisa)
        soup  = requests.get(url)
        soup  = BeautifulSoup(soup.content, 'html.parser')
            
        name_box = soup.find_all('tr')
        name_boxccc=name_box[1]
        name_boxccc = name_boxccc.get_text(strip=True)
        lista_indice=[]
        lista_activo=[]
        lista_divisa=[]
        lista_num_errores=[]
        lista_empresa=[]
        lista_resto=[]

        for i in range(1,len(name_box)-1):
            try:
                lista_indice.append(Index)
                name_boxccc=name_box[i]
                name_boxccc = name_boxccc.get_text(strip=True)
                name_boxccc=name_boxccc.split(sep='.')
                lista_activo.append(name_boxccc[0]+'.'+name_boxccc[1][0:2])
                lista_empresa.append(name_boxccc[1][2:5]+'.'+name_boxccc[2][0:len(name_boxccc[2])])
                lista_resto.append(name_boxccc)
                lista_divisa.append(divisa)

            except:
                lista_num_errores.append(i)

        if len(lista_activo)==len(lista_divisa) & len(lista_activo)==len(lista_empresa) & len(lista_activo)==len(lista_resto):

            df=pd.DataFrame ({'indice':lista_indice,
                            'activo':lista_activo,
                            'divisa':lista_divisa,
                            'resto':lista_resto})
            df['posicion']=np.where(df['resto'].astype(str).str.contains('%', regex=False)==True,1,0)
            df=df[df['posicion']==1]
            df=df.drop(['resto','posicion'],1)

            if n==0:
                dfacum=df
            else:
                dfacum=pd.concat([dfacum, df], axis=0,sort=True)
                dfacum.reset_index(drop=True)
            n=n+1

        else:
            print('El activo '+str(i)+'no se ha podido incorporar por inconsistencias en los datos importados')

    except:
            
        print('Para la referencia '+str(i)+' no se ha podido descargar la informacion')
    
    return dfacum

#%%
dfacum=componentes_indice(tickers_de_indices)
componentes_ibex= dfacum.iloc[:,1]
lista_componentes_ibex= componentes_ibex.tolist()
lista_componentes_ibex
empresas_ibex=[]
for i in lista_componentes_ibex:
    z = str(i[0:-3])
    empresas_ibex.append(z)

# %%
empresas_ibex
#%%
master= empresas_ibex[4:-1]
master
#%%
close = pd.DataFrame(data=None, index=None, columns=None, dtype=None, copy=False)
i=0
for company in tqdm(master):

    df = investpy.get_stock_historical_data(stock= company,
                                            country='Spain',
                                            from_date='01/01/2019',
                                            to_date='01/01/2020')

    i= i+1
    close[i]= df.iloc[:,3]
    #close.append(cierre)
#%%
close.columns=master
# %%
close
# %%

# %%
df = investpy.get_stock_historical_data(stock= 'AMA',
                                            country='Spain',
                                            from_date='01/01/2019',
                                            to_date='01/01/2020')
# %%
