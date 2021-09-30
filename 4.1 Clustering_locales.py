# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 10:02:19 2021

@author: carlo
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from yellowbrick.cluster import KElbowVisualizer


idealista = pd.read_json('data_idealista.json')
locales = idealista[['CP', 'price', 'size', 'latitude', 'longitude']]
data = pd.read_csv('poblacion-renta.csv', sep = ';')[['CP', 'Poblacion', 'declaraciones', 'renta bruta media']]
locales = locales.merge(data, left_on = 'CP', right_on = 'CP', how = 'inner')
del data
idealista = idealista.loc[locales.index, :]
df = locales.drop(['latitude', 'longitude'], axis = 1)
tipos = {pos:i for pos, i in enumerate(df.columns)}

# En primer lugar normalizo el dataset

X = df.values
X = np.nan_to_num(X)
cluster = StandardScaler().fit_transform(X)
df_norm = pd.DataFrame(cluster).rename(columns=tipos)


# E·ncuentro el número adecuado de clusters
error_cost=[]

for i in range(3, 10):
  KM = KMeans(n_clusters=i, max_iter=100)
  try:
    KM.fit(df_norm)

  except ValueError:
    print('Error on line', i)

  # Calculo el error cuadratico medio
  error_cost.append(KM.inertia_ / 100)

# represento los valores del nl número de clusters frente al error
plt.figure(figsize=(13,7))
plt.plot(range(3,10), error_cost, color='r', linewidth=3)
plt.xlabel('Number of k clusters')
plt.ylabel('Squared Error (Cost)')
plt.grid(color='white', linestyle='-', linewidth=2)

plt.show()

# Instantiate the clustering model and visualizer
model = KMeans()
visualizer = KElbowVisualizer(model, k=(3,11))

visualizer.fit(X)

# K=6

# set number of clusters
kclusters = 6

# k-means clustering
kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(df_norm)
idealista.insert(0, 'cluster', kmeans.labels_)
locales.insert(0, 'cluster', kmeans.labels_)

del cluster, df, df_norm, error_cost, i, tipos, X, kclusters

from pyproj import Proj
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

locales.loc[:, ['x', 'y']] = 0.0
for i in range(locales.shape[0]):
    x, y =  p.latlon_utm(locales.at[i, 'latitude'], locales.at[i, 'longitude'])
    locales.at[i, 'y'] = y
    locales.at[i, 'x'] = x

locales2 = locales.drop(['longitude', 'latitude', 'CP' ], axis = 1).groupby('cluster').mean().reset_index().astype(int)
locales2.drop(['x', 'y'], axis = 1).to_pickle('clustering.pkl')

del x, y, locales2, i, locales

import json
with open('data_idealista_cluster.json', 'w') as fp:
    json.dump(idealista.to_dict('records'), fp)


# =============================================================================
# VISUALIZACION
# =============================================================================

# Matplotlib and associated plotting modules
import matplotlib.cm as cm
import matplotlib.colors as colors
import folium
from geopy.geocoders import Nominatim

address = 'Madrid'
geolocator = Nominatim(user_agent="to_explorer")
location = geolocator.geocode(address)
latitud = location.latitude
longitud = location.longitude

# create map
map_clusters = folium.Map(location=[latitud, longitud], zoom_start=11)

# set color schemes for the clusters
x = np.arange(idealista.cluster.nunique())
ys = [i + x + (i*x)**2 for i in range(idealista.cluster.nunique())]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

# add markers to the map
# markers_colors = []
for lat, lon, cluster in zip(idealista['latitude'], idealista['longitude'], idealista['cluster']):
    label = folium.Popup(' Cluster ' + str(cluster))
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        color=rainbow[cluster-1],
        fill=True,
        fill_color=rainbow[cluster-1],
        fill_opacity=0.7).add_to(map_clusters)
       
map_clusters

















