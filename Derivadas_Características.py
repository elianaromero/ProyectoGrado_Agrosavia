# -*- coding: utf-8 -*-
"""
Created on Fri Sep 17 23:08:09 2021

@author: edwin

script para aumentar el vector de caracteristicas a partir de la base de datos de firmas espectrales de sentinel 2
y muestras carbosol, se realizan los siguientes procedimientos.
    1. Obtención de la primera derivada de la firma espectral
    2. Obtencion de la segunda derivada 
    3. Eliminación del continuo.
"""

import pandas as pd

def derivada(y1, y2, l1, l2):
    """
    
    Parameters
    ----------
    y1 : TYPE
        Valor de radiancia de la banda actual.
    y2 : TYPE
        Valor de radiancia de la muestra anterior.
    l1 : TYPE
        Longitud de onda de la muestra actual.
    l2 : TYPE
        Longitud de onda de la muestra anterior.

    Returns
    -------
    float.
        Difference formula: se utiliza la formula de diferencia o deridava hacia adelante con paso h
        donde h es la distancia entre muestras que para este caso seria la distancia entre longitudes de onda
        f'(a) = (f(a+h) - f(a))/h
    """
    pendiente = (y2 - y1)/(l2 - l1)
    return pendiente

tabla_features_labels = pd.read_csv('E:/User/Escritorio/SEMESTRE 9/PROY GRADO 1/Python Imagenes/Bases Datos Imagenes/Features_Labels_OM.csv',index_col=0)

# Llongitudes de onda de la banda central de sentinel 2A
longitudes = [4.427E-07,4.924E-07,5.598E-07,6.646E-07,7.041E-07,7.405E-07,7.828E-07,8.328E-07,8.647E-07,9.451E-07,1.3735E-06,1.6137E-06,2.2024E-06]

# Vector donde se almacenaran las derivadas
first_derivative = pd.DataFrame(columns=['B1dx','B2dx','B3dx','B4dx','B5dx','B6dx','B7dx','B8dx','B9dx','B10dx','B11dx','B12dx'])

#-------- CALCULO DE LA PRIMERA DERIVADA
for index, row in tabla_features_labels.iterrows():
     temporal = []         # Lista temporal para almacenar las derivadas de la fila
     for j in range(12):
         l1 = longitudes[j]
         l2 = longitudes[j+1]
         y1 = tabla_features_labels.iloc[index, j+3] # Primer valor de radiancia
         y2 = tabla_features_labels.iloc[index, j+4] # Segundo valor de radiancia
         dx = derivada(y1, y2, l1, l2)
         temporal.append(dx) # Agrega a la fila de derivadas un valor columna a columna en cada pasada
     first_derivative.loc[index] = temporal # Agrega al dataframe de derivadas la fila completa 

for n in range(1,13,1):
    tabla_features_labels.insert(15+n,'B'+str(n)+'dx',first_derivative['B'+str(n)+'dx'])

# Vector donde se almacenaran las segundas derivadas
second_derivative = pd.DataFrame(columns=['B1dx2','B2dx2','B3dx2','B4dx2','B5dx2','B6dx2','B7dx2','B8dx2','B9dx2','B10dx2','B11dx2'])

#-------- CALCULO DE LA SEGUNDA DERIVADA
for index, row in tabla_features_labels.iterrows():
     temporal = []         # Lista temporal para almacenar las derivadas de la fila
     for j in range(11):
         l1 = longitudes[j]
         l2 = longitudes[j+1]
         y1 = tabla_features_labels.iloc[index, j+16] # Primer valor de la primera derivada
         y2 = tabla_features_labels.iloc[index, j+17] # Segundo valor de la primera derivada
         dx2 = derivada(y1, y2, l1, l2)
         temporal.append(dx2) # Agrega a la fila de derivadas un valor columna a columna en cada pasada
     second_derivative.loc[index] = temporal # Agrega al dataframe de derivadas la fila completa 

for n in range(1,12,1):
    tabla_features_labels.insert(27+n,'B'+str(n)+'dx2', second_derivative['B'+str(n)+'dx2'])

# HABILITAR Linea para guardado de los datos
#tabla_features_labels.to_csv('E:/User/Escritorio/SEMESTRE 9/PROY GRADO 1/Python Imagenes/Bases Datos Imagenes/Features_Labels_OM_derivatives.csv')


