# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 11:30:40 2019

@author: cmore
"""
import pandas as pd
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns

#datos_df = pd.read_json('restaurantes_trip_new.json')

#datos = pd.read_pickle('restaurantes_trip_DF_clean_ok.pkl')
#datos = pd.read_pickle('restaurantes_trip_DF.pkl')

datos = pd.read_json('data_tripadvisor.json')
col_names = list(datos.columns.values)

# busqueda de Nan

datos.isnull().sum()
datos.fillna(0,inplace=True)
#datos1 = datos.to_dict(orient='index')
datos = datos.to_dict(orient='list')

# =============================================================================
# MAPEO calle_web
# =============================================================================
import re

ori = [['\|',','],['\.',''],['av\.','avenida'],['av ','avenida'],['avda','avenida'],[' avd ','avenida '],
        ['pl ','plaza '],['pl\. ','plaza '],['sta ','santa '],['local ',''],['cc gavia',''],['bis',''],
        ['nº',''],['s/n',''],['planta',''],['local',''],['bajo',''],['º',''],['ª',''],
        ['portal',''],['no:',''],['ctra','carretera'],['gral','general'],['dcha',''],
        ['izq ',' '],['plaze','plaza'],['puerta',''],['c/','calle']]

limp1 = ['#','esq\s',',','planta','portal','bajo']
         
Tipo = ["calle","avenida","paseo","bulevar","glorieta","plaza","carretera","ronda","travesia"]

for index,i in tqdm(enumerate(datos['calle_web'])):
    i = str(i)
    
    i = i.lower().replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u').replace('à','a')
    i = i.replace('madrid','').replace('españa','')
    try:
        cp=re.findall('\d{5}',i)[0]
        i = re.sub(cp,'',i)
    except:
        cp='0'
    
    try:
        num = re.findall('\d+',i)[0]
        i = re.sub(num,'',i)
    except:
        num='0'
    
    for j in limp1:
        i = re.sub(j+'..+','',i)
    for j in ori:
        i = re.sub(j[0],j[1],i)
        if i =='':
            next
    tipo = []
    for j in Tipo:
        try:
            tipo.append(re.findall(j,i)[0])
        except:
            next
    for j in Tipo:
        i = re.sub(j,'',i)
    if tipo ==[]:
        tipo = ['calle']
    i=i.strip(',').strip()
    i=re.sub(',..+','',i)
    i=re.sub('-..+','',i)
    try:
        datos['calle_tipo'].append(tipo)
        datos['calle_nom'].append(i)
        datos['calle_num'].append(num)
        datos['calle_cp'].append(cp)
    except:
        datos['calle_tipo']=[tipo]
        datos['calle_nom']=[i]
        datos['calle_num']=[num]
        datos['calle_cp']=[cp]
        
no_reclamado ={}
for pos,i in enumerate(datos['calle_nom']):
    if i =="":
        eliminar={}
        for j in datos:
            eliminar[j] = datos[j][pos]
        no_reclamado[pos] = eliminar

z = list(no_reclamado.keys())
z.sort(reverse=True)            
for k in z:
    for l in datos:
        datos[l].pop(k)

datos.pop('calle_web')

# =============================================================================
# Mapeo de precio web
# =============================================================================

regex = [['á','a'],['é','e'],['í','i'],['ó','o'],['ú','u'],['de ',''],['minoria',''],
         ['opciones',''],['vegetarianas','vegano'],['veganas','vegano'],['con cerveza artesanal',''],
         ['restaurante',''],['comida en la calle',''],['/','']]

tags ={}

for i in datos['Precio_web']:
    
    try:
        for j in i.split(','):
            if j[0] == '€':
                next

            else:
                base = j.strip()
                for k in regex:
                    j = j.lower()
                    j =re.sub(k[0],k[1],j).strip()
                if j not in tags:
                    tags[base] = j
    except:
        next

for i in tags.values():
    datos[i] = [0 for x in range(len(datos['Precio_web']))]
    
for pos,i in enumerate(datos['Precio_web']):   
    for j in tags:
        if type(i) != str:
            continue
        i2 = i.split(',')
        i2 = [x.strip() for x in i2]

        if j in i2:
            datos[tags[j]][pos] = 1

for i in set(tags.values()):
    x = datos[i]
    datos.pop(i)
    datos['tipo_'+i] = x
     
datos.pop('Precio_web')   
            
# =============================================================================
# max_price y min_price
# =============================================================================

datos['precio_medio'] = [0 for x in range(len(datos['max_price']))]

for pos,i in enumerate(datos['max_price']):
    
    try:
        datos['max_price'][pos] = int(i)
        datos['min_price'][pos] = int(datos['min_price'][pos])
        
    except:
        datos['min_price'][pos] = 0
        
    datos['precio_medio'][pos] = (datos['max_price'][pos] + datos['min_price'][pos]) / 2
    
# =============================================================================
# Mapeo rating     
# =============================================================================
        
for pos,i in tqdm(enumerate(datos['rating'])):
    temp = int(re.sub('\.','',i.split()[0]))
    datos['rating'][pos] = int(re.sub('\.','',i.split()[0]))
       
datos.pop('ranking_web')

# =============================================================================
# ratings_web
# =============================================================================

ratings = []
for i in datos['ratings_web']:
    try:
        for j in i:
            j='r_'+j.lower()
            if j.lower() not in ratings:
                ratings.append(j.lower())
    except:
        next

for i in ratings:
    datos[i] = [0 for x in range(len(datos['ratings_web']))]
    
for pos,i in enumerate(datos['ratings_web']):
    
    try:
        for j in i:
            datos['r_'+j.lower()][pos] = int(i[j])
    except:
        next
            
datos.pop('ratings_web')    

# =============================================================================
# review_count
# =============================================================================

for pos,i in enumerate(datos['review_count']):
    datos['review_count'][pos] = int(re.findall('\d+',i)[0])
    
del Tipo,base,cp,eliminar,limp1,no_reclamado,num,ori,ratings,regex,tipo,z,i,i2,index,pos,tags,temp,j,k,l,x
    
datos.pop('nombre_web')    
datos.pop('rango_precios')

datos = pd.DataFrame(datos)
col_names_final = list(datos.columns.values)
# datos.to_pickle('datos_tripadvisor.pkl')
del col_names, col_names_final
 

# =============================================================================
# ------------- LIMPIAMOS LOS TIPOS DE RESTAURANTES ---------------------------
# =============================================================================

# trip = pd.read_pickle('restaurantes_trip_DF_todas_las_calles.pkl')
trip = datos.copy()
datos = trip.to_dict('list')


tipos = []

for i in datos:
    if i[:4] == 'tipo':
        tipos.append(i)
        
blancos = []        
for pos,i in enumerate(datos['nombre']):
    suma = 0
    for j in tipos:
        suma += datos[j][pos]
    if suma == 0:
        blancos.append(datos['nombre'][pos])


# tipos = []

# for i in trip.columns.values:
#     if i[0:4] == 'tipo':
#         tipos.append(i)
        
# Cuento la frecuencia con la que aparece cada tipo de comida
valores = {}
for i in tipos:
    if sum(trip[i]) > 0:
        valores[i] = sum(trip[i])

# Hago una lista con las posiciones de cada tipo de comida
rests = {}
for j in tipos:
    rests[j] = datos[j]

# =============================================================================
# # busco para categoría de restaurantes las coincidencias con otras categorías
# =============================================================================
    
# En primer lugar miro para cada categoría si el restaurante está en más categorías  y cuántas son

cat_comunes = {}            
for i in tqdm(rests.keys()):
    cat_comunes[i] = []

    for pos,j in enumerate(datos[i]):
        suma = 0
        if j == 1:
            for k in rests.keys():
                if k != i:
                    suma += datos[k][pos]
        cat_comunes[i].append(suma)

# En segundo lugar presento los restaurantes de cada categoría en cuántas otras categorías está:
cat_comunes2 = {}            
for i in tqdm(rests.keys()):
    cat_comunes2[i] = []

    for pos,j in enumerate(datos[i]):
        suma = 0
        if j == 1:
            for k in rests.keys():
                if k != i:
                    suma += datos[k][pos]
            cat_comunes2[i].append(suma)        
        
# =============================================================================
# Eliminamos las categorias que no son útiles:
# =============================================================================

cat_eliminar= ['sopas','cafe','bar','comida rapida','tienda gourmet','vinoteca','comedor','pub','street food']
for i in cat_eliminar:
    rests.pop('tipo_'+i)
    
# juntamos las catregorías similares
# Estas categorías representan tipologías similares
cat_juntar = {'india':['balti'],'china':['yunnan','fujian'],'japonesa':['sushi'],
              'Europa_oeste':['alemana','austriaca','belga','britanica','centroeuropea','francesa','griega','irlandesa','portuguesa','suiza'],
              'Europa_este':['albanesa','armenia','escandinava','europa oriental','georgiana','israeli','polaca','rumana','rusa','sueca','ucraniana'],
              'Asia_oeste':['turca','persa','nepali','oriente medio'],
              'Asiatica':['afgana','asia central','bangladeshi','coreana','filipina','indonesia','pakistani','polinesia','tailandesa','taiwanesa','tibetana','vietnamita','australiana','asiatica',],
              'Sur_americana':['brasileña','caribeña','centroamericana','chilena','colombiana','cubana','ecuatoriana','latina','salvadoreña','sudamericana','venezolana'],
              'Africana':['africana','egipcia','etiope','libanesa','marroqui'],
              'Norte_Americana':['canadiense','cajun y criolla','hawaiana','americana']
              }

for i in tqdm(cat_juntar):
    try:
        x = rests['tipo_'+i]
    except:
        rests['tipo_'+i] = [0 for x in range(len(rests['tipo_china']))]
    for k in cat_juntar[i]:
        for pos,j in enumerate(rests['tipo_'+k]):
            if j == 1:
                rests['tipo_'+i][pos] = 1
        rests.pop('tipo_'+k)
        
valores2 = {}
for i in rests.keys():
    if sum(rests[i]) > 0:
        valores2[i] = sum(rests[i])

del cat_comunes,cat_comunes2,cat_eliminar,cat_juntar,i,j,k,pos,suma,tipos,valores,x

# =============================================================================
# SVD
# =============================================================================
rests_DF = pd.DataFrame(rests).values

from sklearn.utils.extmath import randomized_svd
U, Sigma, VT = randomized_svd(rests_DF,
                            n_components = 4,    # Number of singular values and vectors to extract.
                            n_oversamples  = 4,  # Smaller number can negatively impact the quality of approximation of singular vectors and singular values.
                            n_iter = 4)          # Number of power iterations. It can be used to deal with very noisy problems.

V = np.transpose(VT)
v_DF = pd.DataFrame(V)

#import matplotlib.pyplot as plt
#import seaborn as sns

sns.set()

plt.plot(Sigma)

columnas = list(valores2.keys())

#cluster0 = list(v_DF.iloc[:,0])
#cluster0_=cluster0
#cluster0_.sort(reverse=True)

v_dict ={}
for i in range(V.shape[1]):
    v_dict[i]=list(v_DF.iloc[:,i])

clusters ={}
orden = list(valores2.keys())

for i in range(V.shape[1]):
    
    c = list(v_DF.iloc[:,i])
    c.sort(reverse=True)
    lista=[]
    for j in c:
        lista.append(orden[v_dict[i].index(j)])
    clusters[i] = lista

V_DF = pd.DataFrame(V)

# Normalizado de matriz--------------------------------------------------------

from numpy import eye, asarray, dot, sum, diag
from numpy.linalg import svd

# Para que se noten más las diferencias entre los distintos agrupamientos
def varimax(Phi, gamma = 1, q = 20, tol = 1e-6):
   p,k = Phi.shape
   R = eye(k)
   d=0
   for i in range(q):
       d_old = d
       Lambda = dot(Phi, R)
       u,s,vh = svd(dot(Phi.T,asarray(Lambda)**3 - (gamma/p) * dot(Lambda, diag(diag(dot(Lambda.T,Lambda))))))
       R = dot(u,vh)
       d = sum(s)
       if d/d_old < tol: break
   return dot(Phi, R)

V_vari = varimax(V_DF)
# No aporta ninguna información útil

del c, columnas,i,j,lista,orden,v_dict,valores2,U,V,Sigma,V_vari,clusters,rests_DF,trip,v_DF

# ------ ACTUALIZO LA BASE DE DATOS ------------------------------------------

datos = pd.DataFrame(datos)

for i in datos.columns.values:
    
    if i[:5] =='tipo_':
        
        datos.drop(columns = [i], inplace = True)

datos = datos.to_dict('list')       

for i in rests:
    datos[i] = rests[i]

del i

#Analizo la información que tenemos en este momento ---------------------------

cat_comunes = {}
          
for i in tqdm(rests.keys()):
    cat_comunes[i] = []

    for pos,j in enumerate(datos[i]):
        suma = 0
        if j == 1:
            for k in rests.keys():
                if k != i:
                    suma += datos[k][pos]
        cat_comunes[i].append(suma)

# En segundo lugar presento los restaurantes de cada categoría en cuántas otras categorías está:
cat_comunes2 = {}            
for i in tqdm(rests.keys()):
    cat_comunes2[i] = []

    for pos,j in enumerate(datos[i]):
        suma = 0
        if j == 1:
            for k in rests.keys():
                if k != i and datos[k][pos] != 0:
                    suma += datos[k][pos]
                    cat_comunes2[i].append(suma) 

del i,j,k,pos,rests,suma
datos= pd.DataFrame(datos)
# datos.to_pickle('restaurantes_trip_DF_categorizado.pkl')

# =============================================================================
# REDUCCIÓN A UNA ÚNICA CATEGORÍA POR RESTAURANTE
# =============================================================================

datos = datos.to_dict('list')

prioridad = ['Europa_oeste','Europa_este','Asia_oeste','Asiatica','Sur_americana',
               'Africana','Norte_Americana','española','argentina','india','mexicana',
               'peruana','japonesa','china','italiana','vegano','marisco','pizza',
               'asador','barbacoa','mediterranea','europea','contemporanea','fusion',
               'internacional','saludable','sin gluten']

# analizo cuántos restaurantes están en varias categorías principales:
for i in prioridad:
    cont = 0
    for pos, j in enumerate(datos['tipo_'+i]):
        if j == 1:
            for k in prioridad:
                if datos['tipo_'+k][pos] == 1 and i != k:
                    cont += 1
                    # print(cont,',',pos,i,k,datos['Unnamed: 0'][pos])
                
#reduzco los restaurantes a tener un sólo tipo de comida.   
                   
for i in prioridad:
    
    for pos, j in enumerate(datos['tipo_'+i]):
        
        if j == 1:
            
            for k in prioridad:
                
                if datos['tipo_'+k][pos] == 1 and i != k:
                    
                    datos['tipo_'+k][pos] = 0      

datos= pd.DataFrame(datos)
datos.to_pickle('datos_tripadvisor.pkl')        
        
