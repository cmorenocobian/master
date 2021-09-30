# -*- coding: utf-8 -*-
"""
Created on Wed Sep 29 12:20:20 2021

@author: carlo
"""
import pandas as pd
import geopandas as gpd
from pyproj import Proj
from tqdm import tqdm

locales = pd.read_json('data_idealista_cluster.json')
rest = pd.read_pickle('restaurantes_geo.pkl')

rest = rest.drop('index', axis =1).reset_index(drop=True)

class conversion:
    """Función para pasar de latitud y longitud a UTM y viceversa"""
    
    def __init__(self, zone=30):
        self.zone = zone
    
    def latlon_utm(self, lat, lon):
        """Latitude and longitude to UTM"""
        myProj = Proj("+proj=utm +zone="+str(self.zone)+",\
        +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs") #north for north hemisphere
        UTMx, UTMy = myProj(lon, lat)
        return UTMx, UTMy
    
    def utm_latlon(self, x, y):
        """UTM to latitude and longitude"""
        myProj = Proj("+proj=utm +zone="+\
        str(self.zone)+", +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
        lon, lat = myProj(x, y,inverse=True)
        return lat, lon

# comprobación de funcionamiento de la clase
p = conversion()

rest.loc[:, ['x', 'y']] = 0.0
for i in tqdm(range(rest.shape[0])):
    x, y =  p.latlon_utm(rest.at[i, 'latitud'], rest.at[i, 'longitud'])
    rest.at[i, 'x'] = x
    rest.at[i, 'y'] = y


locales.loc[:, ['x', 'y']] = 0.0
for i in tqdm(range(locales.shape[0])):
    x, y =  p.latlon_utm(locales.at[i, 'latitude'], locales.at[i, 'longitude'])
    locales.at[i, 'x'] = x
    locales.at[i, 'y'] = y
del x, y

rest = gpd.GeoDataFrame(rest, geometry=gpd.points_from_xy(rest.x, rest.y))
locales = gpd.GeoDataFrame(locales, geometry=gpd.points_from_xy(locales.x, locales.y))
# s= gpd.GeoSeries(rest['geometry'])
# d=rest.distance(locales.at[0, 'geometry'])

tipo = [pos for pos, i in enumerate(list(rest['tipo_fusion'])) if i == 1]
d=[]
for i in tqdm(range(locales.shape[0])):
    d.append(list(rest.distance(locales.at[i, 'geometry'])))

eleccion=[]
for local,i in tqdm(enumerate(d)):
    # break
    # número de restaurantes del mismo tipo a menos de 500 m
    same= len([j for pos,j in enumerate(i) if j < 400 and pos in tipo])
    # Número de restaurantes más próximos
    dist = [pos for pos,j in enumerate(i) if j < 500 and pos not in tipo]
    
    if same>1 and len(dist)<100:
        eleccion.append([local, same, len(dist), dist])
    
# del dist, i, same, tipo, d



local=locales.loc[[i[0] for i in eleccion],:].drop_duplicates(subset=['x', 'y'])
local.to_pickle('locales.pkl')

# si de entre estos locales seleccionamos que deba tener más de 200 m2 pero menos de 600
# y la inversión no permite unos costes en alquiler superiores a 5000€ mensuales
# local=pd.read_pickle('locales.pkl')
local = local.loc[(local['price'] < 10000) & (local['size'] > 200) & (local['size'] < 600)]

# De estos locales podemos analizar la competencia
pmax=30
dif=pmax


for i in eleccion:
    if i[0] in  local.index:
        x= pd.DataFrame(rest.loc[i[-1], ['media', 'rating', 'review_count','Poblacion', 
                              'Hombres', 'Mujeres', 'declaraciones', 'renta bruta media']].mean()).T
        
        if pmax - x.at[0,'media'] < dif:
            local_elegido = local.at[i[0], 'url']
    
print(local_elegido)
    



