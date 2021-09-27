# -*- coding: utf-8 -*-
"""
Created on Tue Sep 21 19:06:29 2021

@author: carlo
"""
import pandas as pd
import numpy as np
import fuzzywuzzy
from fuzzywuzzy import process
# import chardet
from tqdm import tqdm

np.random.seed(0)

tramero = pd.read_excel('nomenclator.xls')
# tripadvisor =  pd.read_json('data_tripadvisor.json')
tripadvisor = pd.read_pickle('datos_tripadvisor.pkl')
# tenedor = pd.read_json('data_tenedor.json')
tenedor = pd.read_pickle('data_tenedor.pkl')

## unificar nombres restaurantes

nombres_tripadvisor = list(map(lambda x: x.lower().strip(),  tripadvisor['nombre'].unique()))
nombres_tenedor = list(map(lambda x: x.lower().strip(),  tenedor['nombre'].unique()))
  
nombres_dict = {}

for element in tqdm(nombres_tenedor):  
    matches = process.extract(element,
                            nombres_tripadvisor, 
                            limit=3, 
                            scorer=fuzzywuzzy.fuzz.token_set_ratio)
    nombres_dict[element] = matches
    
    parecidos = []
    no_parecidos = []
    for element in nombres_dict:
        if nombres_dict[element][0][1] > 90:
            parecidos.append([element, nombres_dict[element][0][0]])
        elif nombres_dict[element][0][1] <90:
            no_parecidos.append([element, nombres_dict[element][0][0]])

for pos, i in tqdm(enumerate(parecidos)):

    if i in nombres_tripadvisor:
        index=nombres_tripadvisor.index(i)
        tripadvisor.at[index, 'nombre'] = parecidos[pos][1]
        
    if i in nombres_tenedor:
        index=nombres_tenedor.index(i)
        tenedor.at[index, 'nombre'] = parecidos[pos][1]
        
del element, i, matches, nombres_dict, no_parecidos, nombres_tenedor, nombres_tripadvisor, parecidos, pos


# Unificar nombres de calles
# nombres_calles = list(set(tramero['dsvial']))
nombres_calles = list(map(lambda x: x.lower().strip(), tramero['dsvial'].unique()))
calles_tripadvisor = list(map(lambda x: x.lower().strip(),  tripadvisor['calle_nom'].unique()))
calles_tenedor = list(map(lambda x: x.lower().strip(),  tenedor['calle'].unique()))  

calles_dict = {}

for element in tqdm(calles_tenedor):  
    matches = process.extract(element,
                            nombres_calles, 
                            limit=3, 
                            scorer=fuzzywuzzy.fuzz.token_set_ratio)
    calles_dict[element] = matches
    
    parecidos = []
    no_parecidos = []
    for element in calles_dict:
        if calles_dict[element][0][1] > 90:
            parecidos.append([element, calles_dict[element][0][0]])
        elif calles_dict[element][0][1] <90:
            no_parecidos.append([element, calles_dict[element][0][0]])

for pos, i in tqdm(enumerate(parecidos)):

    if i in calles_tenedor:
        index=calles_tenedor.index(i)
        tenedor.at[index, 'nombre'] = parecidos[pos][1]
        
calles_dict = {}

for element in tqdm(calles_tripadvisor):  
    matches = process.extract(element,
                            nombres_calles, 
                            limit=3, 
                            scorer=fuzzywuzzy.fuzz.token_set_ratio)
    calles_dict[element] = matches
    
    parecidos = []
    no_parecidos = []
    for element in calles_dict:
        if calles_dict[element][0][1] > 90:
            parecidos.append([element, calles_dict[element][0][0]])
        elif calles_dict[element][0][1] <90:
            no_parecidos.append([element, calles_dict[element][0][0]])

for pos, i in tqdm(enumerate(parecidos)):

    if i in calles_tripadvisor:
        index=calles_tripadvisor.index(i)
        tenedor.at[index, 'nombre'] = parecidos[pos][1]

# Ahora realizo la unión entre los dos datasets

calles_dict = {}
calles_tripadvisor = list(map(lambda x: x.lower().strip(),  tripadvisor['calle_nom'].unique()))
calles_tenedor = list(map(lambda x: x.lower().strip(),  tenedor['calle'].unique()))  

for element in tqdm(calles_tripadvisor):  
    matches = process.extract(element,
                            calles_tenedor, 
                            limit=3, 
                            scorer=fuzzywuzzy.fuzz.token_set_ratio)
    calles_dict[element] = matches
    
    parecidos = []
    no_parecidos = []
    for element in calles_dict:
        if calles_dict[element][0][1] > 90:
            parecidos.append([element, calles_dict[element][0][0]])
        elif calles_dict[element][0][1] <90:
            no_parecidos.append([element, calles_dict[element][0][0]])

for pos, i in tqdm(enumerate(parecidos)):

    if i in calles_tripadvisor:
        index=calles_tripadvisor.index(i)
        tenedor.at[index, 'nombre'] = parecidos[pos][1]
    if i in calles_tenedor:
        index=calles_tenedor.index(i)
        tenedor.at[index, 'nombre'] = parecidos[pos][1]

import geopandas as gdp
import shapely
tenedor = tenedor.join(tramero[['cdtvia', 'dsvial', 'numero', 'latitud', 'longitud']], left_on = ['tipo', 'calle', 'numero'], right_on = ['cdtvia', 'dsvial', 'numero'], how = 'right')
tripadvisor = tripadvisor.join(tramero[['cdtvia', 'dsvial', 'numero', 'latitud', 'longitud']], left_on = ['cdtvia', 'dsvial', 'numero'], right_on=['calle_tipo', 'calle_nom', 'calle_num'], how = 'right')

tenedor.loc[:, 'coords'] = tenedor.appply(lambda x: shapely.Point(x['longitud'], x['latitud']))
tenedor= gdp.Geopandas(tenedor, geometry='coords')

tripadvisor.loc[:, 'coords'] = tripadvisor.appply(lambda x: shapely.Point(x['longitud'], x['latitud']))
tripadvisor= gdp.Geopandas(tripadvisor, geometry='coords')

# Creo una función que busca el punto más cercano y la distancia entre ellos
# Con esta información podré unificar los restaurantes de los dos datasets

from scipy.spatial import cKDTree

def ckdnearest(gdA, gdB):

    nA = np.array(list(gdA.geometry.apply(lambda x: (x.x, x.y))))
    nB = np.array(list(gdB.geometry.apply(lambda x: (x.x, x.y))))
    btree = cKDTree(nB)
    dist, idx = btree.query(nA, k=1)
    gdB_nearest = gdB.iloc[idx].drop(columns="geometry").reset_index(drop=True)
    gdf = pd.concat(
        [
            gdA.reset_index(drop=True),
            gdB_nearest,
            pd.Series(dist, name='dist')
        ], 
        axis=1)

    return gdf

restaurantes = ckdnearest(tenedor, tripadvisor)
restaurantes = pd.DataFrame(restaurantes).drop(axis= ['coords_x', 'coords_y'])
# Establezco como distancia máxima entre restaurantes 50 m
restaurantes = restaurantes.loc[restaurantes['dist'] < 0.05]
restaurantes.to_pickle('restaurantes.pkl')



