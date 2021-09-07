# -*- coding: utf-8 -*-
"""
Created on Thu Aug 12 17:17:02 2021

@author: edwin

Este script descarga de la tabla de propiedades con lat,lon la imagen multiesprectral y la guarda en el disco
"""
#librerias
import cv2
import os
import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib as plt
import seaborn as sns
import copy
import geopy                 # librerias para el calculo de distancias geodesicas y transformaciones
import geopy.distance
from sentinelhub import WebFeatureService, BBox, CRS, DataCollection, SHConfig   # libreria para el acceso a SH

#-----------CONFIGURACION DE MI CUENTA DE SENTINEL HUB-------
config = SHConfig() 
config.sh_client_id = '776adf5c-617a-4f21-bd45-bcd6c18853e0'         # usuario que me asigno sentinel hub
config.sh_client_secret = '8T)RFCc7-b]+qd7CD|ZZQ+&ZRYSWu/hRp4?AhNSy' # clave de sentinel hub

# verificacion de que si se escribieron las credenciales
if config.sh_client_id == '' or config.sh_client_secret == '':
    print("Warning! To use Sentinel Hub Process API, please provide the credentials (client ID and client secret).")
    
#------------ LIBRERIA PARA EL MANEJO DE DATOS CON SH-----------
from sentinelhub import MimeType, CRS, BBox, SentinelHubRequest, SentinelHubDownloadClient, \
    DataCollection, bbox_to_dimensions, DownloadRequest
import python_utils


# direccion de la tabla de etiquetas
ruta = "/home/edwin/Desktop/Imagenes Satelitales/carb_labels.csv"

carb_labels = pd.read_csv(ruta, delimiter=',' , index_col=0)     # cargo la tabla de etiquetas
carb_labels_copy = copy.deepcopy(carb_labels)         #genero una copia real de los datos

carb_statistics = carb_labels_copy.describe()

def getImage(latitud, longitud):
    """
    solicita una imagen multiespectral a sentinelHub, recibe como parametros latitud, longitud
    
    Parameters
    ----------
        latitud, longitud

    Returns
    -------
        Imagen en numpy array

    """
    # UN PIXEL
    #------------ Coordenadas del sitio en wgs84 (4 puntos coordenados)------------
    # cero grados es el Norte
    calculo_Bbox = [latitud, longitud] # Genero una caja contenedora de x Km^2 para la imagen satelital 
    start = geopy.Point(calculo_Bbox)   # latitud , longitud
    d = geopy.distance.GeodesicDistance(kilometers = 0.011)   
    endPoint1 = d.destination(point=start, bearing = 180)     # distancia que se recorre hacia abajo
    endPoint1 = d.destination(point=endPoint1, bearing = 270)     # distancia que se recorre hacia izda
    latitud1 = endPoint1.latitude        # Lat y Long de esquina inferior Izda
    longitud1 = endPoint1.longitude
    print('Lat:',latitud1,'-Long:', longitud1) 
    print(endPoint1)
    
    start = geopy.Point(calculo_Bbox)   # latitud , longitud
    d = geopy.distance.GeodesicDistance(kilometers = 0.011)   
    endPoint2 = d.destination(point=start, bearing = 0)     # distancia que se recorre hacia arriba
    endPoint2 = d.destination(point=endPoint2, bearing = 90)     # distancia que se recorre hacia Derecha
    latitud2 = endPoint2.latitude        # Lat y Long de esquina superior derecha
    longitud2 = endPoint2.longitude
    print('Lat:',latitud2,'-Long:', longitud2)
    print(endPoint2)
    
    par_coordenadas = [longitud1,latitud1,longitud2,latitud2] # Cuadro delimitador (coordenadas)
    resolution = 15   # minima resolucion espacial es de 15 metros
    BBox_coordenadas = BBox(bbox=par_coordenadas, crs=CRS.WGS84) # caja de coordenadas
    BBox_size = bbox_to_dimensions(BBox_coordenadas, resolution=resolution) # resolucion de la imagen
    
    print(f'Image shape at {resolution} m resolution: {BBox_size} pixels') 
    
    #------------Script personalizado de los datos de descarga--------

    evalscript_all_bands = """
        //VERSION=3
        function setup() {
            return {
                input: [{
                    bands: ["B01","B02","B03","B04","B05","B06","B07","B08","B8A","B09","B10","B11","B12"],
                    units: "DN"
                }],
                output: {
                    bands: 13,
                    sampleType: "INT16"
                }
            };
        }
    
        function evaluatePixel(sample) {
            return [sample.B01,
                    sample.B02,
                    sample.B03,
                    sample.B04,
                    sample.B05,
                    sample.B06,
                    sample.B07,
                    sample.B08,
                    sample.B8A,
                    sample.B09,
                    sample.B10,
                    sample.B11,
                    sample.B12];
        }
    """
    
    
    
    test_dir ='E:/User/Escritorio/SEMESTRE 9/PROY GRADO 1/Python Imagenes/ubicaciones'  #direccion de la carpeta de guardado
    #-----------Se realiza la solicitud de datos a sentinel hub en todas las bandas espectrales---------
    request_all_bands = SentinelHubRequest(
        data_folder=test_dir,
        evalscript=evalscript_all_bands,
        input_data=[SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L1C,
                time_interval=('2015-06-01', '2020-06-30'),
                mosaicking_order='leastCC')],
        responses=[SentinelHubRequest.output_response('default', MimeType.TIFF)],
        bbox=BBox_coordenadas,
        size=BBox_size,
        config=config
    )
    
    
    #all_bands_img = request_all_bands.get_data(save_data=True)  # Guardado de la imagen Multiespectral
    all_bands_img = request_all_bands.get_data()  # NO Guardado de la imagen Multiespectral
    
    print(f'The output directory has been created and a tiff file with all 13 bands was saved into ' \
          'the following structure:\n')
    return (all_bands_img)

def sueloDesnudoNDVI(image):   
    '''
    para que se considere suelo desnudo el NDVI debe ser menor a 0.1

    Parameters
    ----------
    imagen : TYPE = numpy array
        DESCRIPTION. --> recibe una imagen en formato numpy array normalmente de dimensiones 1,1,13

    Returns 
    -------
       Retorna TRUE si el NDVI es MENOR O IGUAL a 0.1, FALSE si el MAYOR a 0.1

    '''
    banda4 = image[0,0,3]
    print('El valor de la banda 4 es:', banda4, 'tipo de dato:', type(banda4))
    

    banda8= image[0,0,7]
    print('El valor de la banda 8 es:', banda8)

    ndvi = (banda8.astype(float) - banda4.astype(float)) / (banda8 + banda4) #Formula de índice de vegetación de diferencia normalizada.
    print('El NDVI es:', ndvi)
    
    if ndvi <= 0.1:
        a = True
    else:
        a = False
    return(a)
    
    
carb_locations = copy.deepcopy(carb_labels_copy)
#carb_locations.drop(['Carb [%]'], axis=1, inplace=True)

#creacón de la las columnas de la tabla
tabla_features_labels = pd.DataFrame(columns=['lat','long','B1','B2','B3','B4','B5','B6','B7','B8','B8A','B9','B10','B11','B12','Carb [%]'])

#NOTA: Sila descarga es interumpida continuar la descarga desde una muestra despues de la ultima registrada cambiando iloc

#-------------------------------------V Numero de muestra
for index, row in carb_locations.iloc[0:].iterrows():
    long = row['Longitude']
    lat = row['Latitude']
    #print(row['Latitude'], row['Longitude'])
    #getImage(lat, long)
    image = getImage(lat, long)    # getimage genera una lista que dentro tiene un numpy array
    image1 = image[0]              # saco de la lista el numpy y me queda un array of uint16
    print('IMAGEN ES:' ,type(image1))
    print(image1.shape)
    print(image1[0,0,0])
    a = sueloDesnudoNDVI(image1) 
    print('El suelo esta desnudo', a)
    
    if a == True:
        #-- almaceno en variables los valores del pixel de suelo desnudo
        B1 = image1[0,0,0]
        B2 = image1[0,0,1]
        B3 = image1[0,0,2]
        B4 = image1[0,0,3]
        B5 = image1[0,0,4]
        B6 = image1[0,0,5]
        B7 = image1[0,0,6]
        B8 = image1[0,0,7]
        B8A = image1[0,0,8]
        B9 = image1[0,0,9]
        B10 = image1[0,0,10]
        B11 = image1[0,0,11]
        B12= image1[0,0,12]
        carb = row['Carb [%]']
        # Guardo los valores de las bandas en 
        tabla_features_labels = tabla_features_labels.append({'lat':lat,'long':long,'B1':B1, 'B2':B2, 'B3':B3, 'B4':B4,\
                                                              'B5':B5,'B6':B6,'B7':B7,'B8':B8,'B8A':B8A,'B9':B9,'B10':B10,\
                                                              'B11':B11,'B12':B12,'Carb [%]':carb}, ignore_index=True)
    print('el numerdo de muestra es:',index)
    #guardo la tabla actualizada
    tabla_features_labels.to_csv('/home/edwin/Desktop/Imagenes Satelitales/Features_Labels_Carb.csv')
    
   
 






