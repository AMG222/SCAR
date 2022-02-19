import tensorflow as tf
import math
from tensorflow import keras
from tensorflow.keras import backend as K
from tensorflow.keras.metrics import categorical_crossentropy
from tensorflow.keras.layers import Dense, Activation,Dropout,Conv2D, MaxPooling2D,BatchNormalization, Flatten
from tensorflow.keras import regularizers
from tensorflow.keras.optimizers import Adam, Adamax
from tensorflow.keras.models import Model, load_model, Sequential
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import ReduceLROnPlateau
import numpy as np
import pandas as pd
import shutil
import time
import cv2 as cv2
from tqdm import tqdm
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from matplotlib.pyplot import imshow
import os
import seaborn as sns
sns.set_style('darkgrid')
from PIL import Image
from sklearn.metrics import confusion_matrix, classification_report
from IPython.core.display import display, HTML
import logging
logging.getLogger("tensorflow").setLevel(logging.ERROR)

train_dir=r'data/train_new'
test_dir=r'data/test_new'
epochs = 3
maximun= 150
minimun=0
columnas='labels'
d_t = r'./'
img_size=(256,256)
channels=3
batch_size=25
img_shape=(img_size[0], img_size[1], channels)
semilla_random=123

def s(i):    
    return i
def in_col(digfo,maximun,minimun,columnas):
    digfo=digfo.copy()
    lista_muestras=[] 
    grupos=digfo.groupby(columnas)
    for etq in digfo[columnas].unique():        
        grupo=grupos.get_group(etq)
        long_g=len(grupo)         
        if long_g> maximun :
            muestras=grupo.sample(maximun,replace=False,weights=None,random_state=semilla_random,axis=0).reset_index(drop=True)
            lista_muestras.append(muestras)
        elif long_g>= minimun:
            lista_muestras.append(grupo)
    digfo=pd.concat(lista_muestras,axis=0).reset_index(drop=True)
    balance=list(digfo[columnas].value_counts())
    return digfo
def DataAug_save(tr_d,maximun,minimun,columnas,d_t,t_im):
    tr_d=tr_d.copy()
    tr_d=in_col(tr_d,maximun,minimun,columnas)    
    aug_dir=os.path.join(d_t, 'aug')
    if os.path.isdir(aug_dir):
        shutil.rmtree(aug_dir)
    os.mkdir(aug_dir)
    for etq in tr_d['labels'].unique():    
        dir_path=os.path.join(aug_dir,etq)    
        os.mkdir(dir_path)
    total=0
    gen=ImageDataGenerator(
        horizontal_flip=True, 
        vertical_flip=True,  
        rotation_range=20, 
        width_shift_range=0.2,
        height_shift_range=0.2, 
        zoom_range=0.2, 
        brightness_range=(0.5, 0.9)
    )
    grupos=tr_d.groupby('labels') 
    for etq in tr_d['labels'].unique():               
        grupo=grupos.get_group(etq)  
        long_g=len(grupo)   
        if long_g< maximun:
            im_cont=0
            val_max=maximun-long_g
            target_dir=os.path.join(aug_dir, etq)
            generador = gen.flow_from_dataframe(grupo, x_col='filepaths',y_col=None,target_size=t_im,class_mode=None,batch_size=1,shuffle=False,save_to_dir=target_dir,save_prefix='aug-',color_mode='rgb',save_format='jpg')
            while im_cont < val_max:
                imagenes=next(generador)            
                im_cont += len(imagenes)
            total +=im_cont
    if total>0:
        aug_fpaths=[]
        aug_labels=[]
        classlist=os.listdir(aug_dir)
        for klass in classlist:
            classpath=os.path.join(aug_dir, klass)     
            flist=os.listdir(classpath)    
            for f in flist:        
                fpath=os.path.join(classpath,f)         
                aug_fpaths.append(fpath)
                aug_labels.append(klass)
        Fseries = pd.Series(aug_fpaths, name='filepaths')
        Lseries = pd.Series(aug_labels, name='labels')
        aug_df = pd.concat([Fseries, Lseries], axis=1)
        res = pd.concat([tr_d,aug_df], axis=0).reset_index(drop=True)
    else:
        res = tr_d
    return res 
def Obt_val(tr_d,te_d,trs):
    for cate in ('train','test'):
        if cate  == 'train':
            sd=tr_d
        else:
            sd=te_d
        filepaths=[]
        labels=[]    
        for cl in os.listdir(sd):
            cl_d=os.path.join(sd,cl)
            d_l=os.listdir(cl_d)
            for d in d_l:
                filepaths.append(os.path.join(cl_d,d))
                labels.append(cl)
        Fseries = pd.Series(filepaths,name='filepaths')
        Lseries = pd.Series(labels,name='labels')
        if cate == 'train':
            di_d = pd.concat([Fseries, Lseries],axis=1)  
        else:
            test_sep=pd.concat([Fseries, Lseries],axis=1)
             
    strat = di_d['labels']    
    train_sep, valid_sep = train_test_split(di_d,train_size=trs,shuffle=True,random_state=semilla_random,stratify=strat)   
    return train_sep, test_sep, valid_sep

tr_d, test_df, valid_df = Obt_val(train_dir,test_dir,0.8)
res = DataAug_save(tr_d,maximun,minimun,columnas,d_t,img_size)
aux=len(test_df)
test_batch_size = sorted([int(aux/n) for n in range(1,aux+1) if aux % n ==0 and aux/n<=80],reverse=True)[0]
gen_tr = ImageDataGenerator(preprocessing_function = s, horizontal_flip = True).flow_from_dataframe(res,x_col='filepaths',y_col='labels',target_size=img_size,class_mode='categorical',color_mode='rgb', shuffle=True,batch_size=batch_size)
gen_test = ImageDataGenerator(preprocessing_function = s).flow_from_dataframe(test_df,x_col='filepaths',y_col='labels',target_size=img_size, class_mode='categorical',color_mode='rgb',shuffle=False,batch_size=test_batch_size)
gen_val = ImageDataGenerator(preprocessing_function = s).flow_from_dataframe(valid_df,x_col='filepaths',y_col='labels',target_size=img_size,class_mode='categorical',color_mode='rgb',shuffle=True,batch_size=batch_size) 

model = tf.keras.applications.EfficientNetB4(include_top=False, weights="imagenet",input_shape=img_shape, pooling='max') 
aux = keras.layers.BatchNormalization(axis=-1,momentum=0.99,epsilon=0.001)(model.output)
aux = Dense(256,kernel_regularizer = regularizers.l2(l = 0.016),activity_regularizer=regularizers.l1(0.006),bias_regularizer=regularizers.l1(0.006),activation='relu')(aux)
aux = Dropout(rate=.45,seed=semilla_random)(aux)        
output = Dense(len(list(gen_tr.class_indices.keys())),activation='softmax')(aux)
model = Model(inputs=model.input,outputs=output)

model.compile(Adamax(learning_rate=.001), loss='categorical_crossentropy', metrics=['accuracy']) 
reduce_lr = ReduceLROnPlateau(monitor='loss', factor=0.5, patience=10, min_lr=0.001)
his_fit = model.fit(x=gen_tr,  epochs=epochs, verbose=1, callbacks=[reduce_lr],  validation_data=gen_val,validation_steps=None,  shuffle=False,  initial_epoch=0)
test_steps=int(len(test_df)/test_batch_size)
acierto = model.evaluate(gen_test,verbose=1,steps=test_steps,return_dict=False)[1]*100
print(f'accuracy on the test set is {acierto:5.2f} %')