# -*- coding: utf-8 -*-
"""
Created on Tue Aug 28 14:52:41 2021

@author: carlo
"""
import pandas as pd
from pyproj import Proj
from tqdm import tqdm
import folium
from geopy.geocoders import Nominatim


restaurantes = pd.read_pickle('restaurantes.pkl')
restaurantes = restaurantes.drop(['index', 'calle_tipo', 'calle_nom', 'calle_num', 'Tipo Vía', 'Vía', 'geometry', 'NUME_NUME'], axis = 1)
restaurantes.loc[:, ['x', 'y']] = restaurantes[['x', 'y']].astype(float)


poblacion = pd.read_csv('poblacion-renta.csv', sep = ';')
poblacion.loc[:, 'Superficie'] = poblacion['Superficie'].apply(lambda x: x.replace(",", "."))
poblacion.loc[:, 'Superficie'] = poblacion['Superficie'].astype(float)
restaurantes = restaurantes.merge(poblacion, left_on='calle_cp', right_on = 'CP', how = 'left').drop(['calle_cp'], axis = 1)
del poblacion

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

restaurantes.loc[:, ['latitud', 'longitud']] = 0.0
for i in tqdm(range(restaurantes.shape[0])):
    lat, lon =  p.utm_latlon(restaurantes.at[i, 'x'], restaurantes.at[i, 'y'])
    restaurantes.at[i, 'latitud'] = lat
    restaurantes.at[i, 'longitud'] = lon
    
del i, lat, lon, p
restaurantes.drop(['x', 'y'], axis =1).reset_index(drop =False).to_pickle('restaurantes_geo.pkl')



restaurantes = pd.read_pickle('restaurantes_geo.pkl')
address = 'Madrid'
geolocator = Nominatim(user_agent="to_explorer")
location = geolocator.geocode(address)
latitud = location.latitude
longitud = location.longitude

madrid = folium.Map(location=[latitud, longitud], zoom_start=15)

# add markers to map
for lat, lng, postcode in zip(restaurantes['latitud'], restaurantes['longitud'], restaurantes['CP']):
  label = '{}'.format(postcode)
  label=folium.Popup(label)
  folium.CircleMarker(
      [lat,lng],
      radius=8,
      color='blue',
      popup=label,
      fill_color='#3186cc',
      fill=True,
      fill_opacity=0.7

  ).add_to(madrid)

madrid



