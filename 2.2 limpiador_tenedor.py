# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 11:30:40 2019

@author: cmore
"""
import pandas as pd
import numpy as np
from tqdm import tqdm
import re
datos = pd.read_json('data_tenedor.json')
campos = list(datos.columns.values)
#datos = pd.read_pickle('restaurantes_tenedor_DF.pkl')
# busqueda de Nan

datos.isnull().sum()

# =============================================================================
# Mapeo tags
# =============================================================================
tags = []
for indice,i in tqdm(enumerate(datos['tags'])):
    
    for j in i:

        j = j.strip('.').strip('.').replace('Selección Insider - ',"").lower().replace('italianos','italiano').replace('mariscos','marisquería').replace('cocina vegana','vegetariano').replace('mediterráneos',"mediterráneo").replace('pizza',"pizzería").replace('árabe','arabe').replace('japoneses',"japonés").replace('del ','').replace('de ','')
        j = j.replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u')
        if j not in tags:

            tags.append(j)
   
        datos.loc[indice,j] = 1

for i in tags:
    datos[i].fillna(0,inplace = True)
datos.drop(['tags'], axis = 1, inplace = True)
# =============================================================================
# MAPEO DIRECCION
# =============================================================================

#ori = {'Madrid':'','madrid':'','Spain':'','Calle':'calle','c/':'calle',
#       'C/':'calle','Paseo':'paseo','Avenida':'avenida','Av':'avenida','AV':'avenida',
#       'del':'','de':'','el':'','la':'','las':'','los':'','Las':'','Los':'','\s\s+':' '}

#ori = [['madrid',''],['spain',''],['av\.','avenida'],['av','avenida'],['avda','avenida'],[' avd ','avenida '],['del',''],
#        ['de ',''],['el',''],['la',''],['las',''],['los',''],['del',''],['de',''],
#        ['pl ','plaza '],['sta ','santa '],['local ',''],['cc gavia',''],['bis',''],
#        ['nº',''],['s/n',''],['planta',''],['local',''],['bajo',''],['º',''],['ª',''],
#        ['portal',''],['no:',''],['ctra','carretera'],['gral','general'],['dcha',''],['izq ',' '],['plaze','plaza'],['puerta','']]

ori = [['madrid',''],['spain',''],['av\.','avenida'],['av','avenida'],['avda','avenida'],[' avd ','avenida '],
        ['pl ','plaza '],['sta ','santa '],['local ',''],['cc gavia',''],['bis',''],
        ['nº',''],['s/n',''],['planta',''],['local',''],['bajo',''],['º',''],['ª',''],
        ['portal',''],['no:',''],['ctra','carretera'],['gral','general'],['dcha',''],['izq ',' '],['plaze','plaza'],['puerta','']]

#ori3 = [['madrid',''],['spain',''],['av\. ','avenida'],['del ',''],['de ','']]
tipo = ["calle","avenida","paseo","boulevar","glorieta","plaza","carretera","ronda","travesia"]

direccion = datos['direccion'].tolist()

for index,i in tqdm(enumerate(direccion)):

    i = i.lower().replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u').replace('à','a').replace('c/','calle ').replace('pl. ','plaza ')#.replace('sta ','santa ')
    i = re.sub(",","",i)
    i = re.sub("\.","",i)
    i = re.sub(r'\([^)]*\)',"",i)
    i = re.sub("-..+","",i)
    i = re.sub("acceso(...)","",i)
    i = re.sub("mercado de..+"," ",i)
    try:
        cp = re.findall("\d{5}",i)[0]
    except:
        cp = None
    i = re.sub("\d{5}","",i)
    try:
        numero = re.findall("\d+",i)[0]
        i = re.sub("\d+","",i)
        if len(numero) == 4:
            numero = numero[0:2]
    except:
        numero = None

    for j in ori:

        i = re.sub(r'\b'+j[0]+r'\b',j[1],i)
    try:    
        if i.split()[0] in tipo:
            tipo_calle = i.split()[0]
            i = re.sub(i.split()[0],"",i)
        else:
            tipo_calle = "calle"
    except:
        tipo_calle = None

    i = re.sub('\s\s+',' ',i)
    i = i.strip()
    i = re.sub(r' [a-m]\b','',i)
    i = re.sub(r' esq..+',' ',i)
    for j in tipo:
        i = i.replace(j,'')
    datos.loc[index,'tipo'] = tipo_calle
    datos.loc[index,'calle'] = i.strip()
    try:
        datos.loc[index,'numero'] = int(numero)
    except:
        datos.loc[index,'numero'] = 0
        
    try:
        datos.loc[index,'cp'] = int(cp)
    except:
        datos.loc[index,'cp'] = 0

datos.drop(['direccion'], axis = 1, inplace = True)


# =============================================================================
# mapeo precio medio
# =============================================================================
    
for index,i in tqdm(enumerate(datos['precio'])):
    try:
        
        datos.loc[index,'medio'] =  int(re.findall("\d{1,3}",i)[0])
    except:
        datos.loc[index,'medio'] = 0
datos.drop(['precio'], axis = 1, inplace = True)
# =============================================================================
# mapeo oferta
# =============================================================================

for index,i in tqdm(enumerate(datos['oferta'])):
    try:
        if i[0] =='-':
            datos.loc[index,'descuento'] = int(i[1:3])
        elif i[0] =='¡':
            datos.loc[index,'descuento'] = int(i[2:4])
        elif i[0] == int:
            datos.loc[index,'descuento'] = int(i[0:2])
                
    except:
        datos.loc[index,'descuento'] = 0
        
datos['descuento'].fillna(0).astype(int)

datos.drop(['oferta'], axis = 1, inplace = True)    
    
# =============================================================================
# mapeo reviews
# =============================================================================

datos['reviews'] = datos['reviews'].str.replace(r'\D+', '')
datos['reviews']=pd.to_numeric(datos['reviews'], errors='coerce').fillna(0)    

 # =============================================================================
# mapeo rating
# =============================================================================

datos['rating'] = datos['rating'].str.replace(r',', '.').astype(float).fillna(0)       
        
campos = list(datos.columns.values)      
        
del cp, direccion, i,index,indice,j,numero,ori,tags,tipo,tipo_calle
#del a,aux,b,cena,comida,d,desayuno,dias,dias2,dias3,horas,horas2,i,indice,j,k,l1,l2,lista,pos,pos2,ppp,primero,tipos,ultimo,x

datos.to_pickle('data_tenedor.pkl')







