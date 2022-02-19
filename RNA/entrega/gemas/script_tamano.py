"""
Este archivo cambia el tamano de todas las imagenes al tamano cuadrado que se desee en este caso 256x256
y les aplica un edge and cut que se encarga de ajustar el objeto en cuestion a los limites de la imagen
"""
import tensorflow as tf
import numpy as np
#from PIL import Image
import cv2 as cv
import os
sizeI = 256
root='data/'
data = ['train', 'test']
image_list=[]

for data_folder in data:
    dir_list = os.listdir(root + data_folder + '/')
    root_d = root + data_folder + '_new/'
    os.mkdir(root_d)
    for folder in dir_list:
        os.mkdir(root_d + folder)
        for filename in os.listdir(root + data_folder + '/' + folder + '/'):
            file_dir = root + data_folder + '/' + folder + '/' + filename
            im = cv.imread(file_dir)
            im = cv.resize(im, (sizeI, sizeI))
            #im  = edge_and_cut(im)
            cv.imwrite(root_d + folder + '/' + filename, im)
