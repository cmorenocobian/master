# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 10:02:19 2021

@author: carlo
"""
import pandas as pd
import numpy as np
import geopandas as gpd
from pyproj import Proj
from tqdm import tqdm

# locales = pd.read_json('data_idealista.json')
rest = pd.read_pickle('restaurantes_geo.pkl')

rest = rest.drop('index', axis =1).reset_index(drop=True)
tipos = [i for i in rest.columns if "tipo_" in i]
rest=rest.loc[rest['tipo_Asiatica'] ==1].drop(tipos, axis = 1).drop(['nombre', 'CP', 'Superficie', 'Densidad'], axis = 1)
tipos = {pos:i for pos, i in enumerate(rest.columns)}


# En primer lugar normalizo el dataset
from sklearn.preprocessing import StandardScaler
X = rest.values
X = np.nan_to_num(X)
cluster = StandardScaler().fit_transform(X)
df_norm = pd.DataFrame(cluster).rename(columns=tipos)


# E·ncuentro el número adecuado de clusters

from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

error_cost=[]

for i in range(3, 15):
  KM = KMeans(n_clusters=i, max_iter=100)
  try:
    KM.fit(df_norm)

  except ValueError:
    print('Error on line', i)

  # Calculo el error cuadratico medio
  error_cost.append(KM.inertia_ / 100)

# represento los valores del nl número de clusters frente al error
plt.figure(figsize=(13,7))
plt.plot(range(3,15), error_cost, color='r', linewidth=3)
plt.xlabel('Number of k clusters')
plt.ylabel('Squared Error (Cost)')
plt.grid(color='white', linestyle='-', linewidth=2)

plt.show()

from yellowbrick.cluster import KElbowVisualizer

# Instantiate the clustering model and visualizer
model = KMeans()
visualizer = KElbowVisualizer(model, k=(3,11))

visualizer.fit(X)

# K=5

# set number of clusters
kclusters = 5

# run k-means clustering
kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(df_norm)

# check cluster labels generated for each row in the dataframe
kmeans.labels_[0:10]


rest.insert(0, 'cluster', kmeans.labels_)

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
x = np.arange(kclusters)
ys = [i + x + (i*x)**2 for i in range(kclusters)]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

# add markers to the map
# markers_colors = []
for lat, lon, cluster in zip(rest['latitud'], rest['longitud'], rest['cluster']):
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

















