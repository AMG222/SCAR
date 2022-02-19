from __future__ import print_function
import matplotlib.pyplot as plt
import sys
import keras
import numpy as np
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dense, Activation, Reshape, Flatten
from keras.layers import BatchNormalization as BN
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.optimizers import Adam
from keras.layers import GaussianNoise as GN
from keras.callbacks import ReduceLROnPlateau
from keras.callbacks import LearningRateScheduler as LRS
from keras.layers import Conv2D, MaxPooling2D, AveragePooling2D
from keras.utils import np_utils
import keras.applications
from keras.layers import Dropout
from keras.preprocessing.image import ImageDataGenerator
import albumentations as A

import tensorflow as tf

batch_size = 32
epochs = 300
num_classes = 87
image_size = 256
#datagen = ImageDataGenerator(rescale=1 / 255.0)
def Augmentor (img):
    transform = A.Compose([
        A.HorizontalFlip(always_apply=False,p=0.5),
        A.VerticalFlip(always_apply=False,p=0.5),
        A.ShiftScaleRotate(always_apply=False,p=1.0, shift_limit=(-0.05, 0.05), scale_limit=(-0.05, 0.05), rotate_limit=(-180, 180), border_mode=4),
        
        #Definitivamente NO
        #A.Solarize(always_apply=False, p=1.0),
        #A.ToGray(always_apply=False, p=1.0),
        #A.ChannelShuffle(always_apply=False, p=1.0),
        #A.ToSepia(always_apply=False, p=1.0),
        #A.ChannelDropout(always_apply=False, p=1.0),

        A.HueSaturationValue(always_apply=False, p=1.0),
        #A.RandomSnow(always_apply=False, p=1.0),
        #A.Blur(always_apply=False,p=0.2),
        A.RandomBrightnessContrast(always_apply=False,p=0.2),
        #A.CLAHE(always_apply=False,p=1.0),

        #A.ImageCompression(always_apply=False, p=1.0),
        #A.GridDistortion(always_apply=False,p=0.2),
        #A.ElasticTransform(always_apply=False, p=1.0), 
        #A.Posterize(always_apply=False,p=0.2),
        A.CoarseDropout(always_apply=False,p=0.9, max_holes=5, max_height=20, max_width=20, min_holes=1, min_height=1, min_width=1),
        #A.MotionBlur(always_apply=False, p=1.0),
        #A.GaussNoise(always_apply=False,p=1.0),
        A.Equalize(always_apply=False,p=0.2),
        #A.RandomGridShuffle(always_apply=False, p=1.0),

        #A.MultiplicativeNoise(always_apply=False, p=1.0),
        #A.Posterize(always_apply=False, p=1.0),
        #A.RandomFog(always_apply=False, p=1.0),
        A.Downscale(always_apply=False, p=1.0),
        #A.ISONoise(always_apply=False, p=1.0),
        #A.RandomGamma(always_apply=False, p=1.0),
        A.RGBShift(always_apply=False, p=1.0),
    ])
    #img = 255 * img
    img = img.astype(np.uint8)

    transformed = transform(image=img)
    transformed_img = transformed["image"]
      
    transformed_img = transformed_img.astype('float32')
    transformed_img /= 255
    
    return transformed_img

datagen = ImageDataGenerator(
    width_shift_range=0.1,
    height_shift_range=0.1,
    zoom_range=0.2,
    shear_range=0.2,
    rotation_range=360,
    horizontal_flip=True,
    vertical_flip=True,
    #preprocessing_function = Augmentor
    )
"""
datagen = ImageDataGenerator(rescale=1 / 255.0,
    zoom_range=0.2,
    shear_range=0.2,
    width_shift_range=0.2,
    height_shift_range=0.2,
    rotation_range=360,
    horizontal_flip=True,
    vertical_flip=True
)
"""
train = datagen.flow_from_directory(
    directory='./data/train_new/',
    target_size=(image_size, image_size),
    color_mode="rgb",
    batch_size=batch_size,
    class_mode="categorical",
    subset='training',
    shuffle=True,
    seed=42
)
#ver imagenes
"""for _ in range(5):
    img, label = train.next()
    print(img.shape)   #  (1,256,256,3)
    plt.imshow(img[0])
    plt.show()"""
test_datagen = ImageDataGenerator(rescale=1 / 255.0)
test = test_datagen.flow_from_directory(
    directory='./data/test_new/',
    target_size=(image_size, image_size),
    color_mode="rgb",
    batch_size=batch_size,
    class_mode="categorical",
    #subset='validation',
    shuffle=True,
    seed=42
)
if (len(train)==0):
    print("El train no se ha cargado bien")
    sys.exit()
if (len(test)==0):
    print("El test no se ha cargado bien")
    sys.exit()


model = Sequential()

# Model, note the reshape
"""model.add(Flatten(input_shape=(image_size, image_size, 3)))

model.add(Dense(512))
model.add(BN())
model.add(GN(0.3))
model.add(Activation('relu'))

model.add(Dense(1024))
model.add(BN())
model.add(GN(0.3))
model.add(Activation('relu'))"""

# first layer
model.add(Conv2D(32, (3, 3), activation='relu', padding='same', input_shape=(256, 256, 3))) # 32
model.add(MaxPooling2D((2, 2))) #reduce the spatial size of incoming features

# second layer
model.add(Conv2D(64, (3, 3), activation='relu', padding='same')) # 64
model.add(MaxPooling2D((2, 2))) 

# third layer
model.add(Conv2D(128, (3, 3), activation='relu', padding='same')) # 128
model.add(MaxPooling2D((2, 2))) 

# fourth layer
model.add(Conv2D(128, (3, 3), activation='relu', padding='same')) # 128
model.add(AveragePooling2D(pool_size= (2, 2), strides= (2, 2))) 

# fifth layer
model.add(Conv2D(128, (3, 3), activation='relu', padding='same')) # 128
model.add(MaxPooling2D((2, 2))) 

model.add(Flatten())
model.add(Dropout(0.5))
model.add(Dense(512, activation='relu'))                                             # 512
model.add(Dense(87, activation='softmax'))

#model.add(Dense(num_classes, activation='softmax'))

model.summary()

sgd=SGD(learning_rate=0.1, decay=0.0, momentum=0.0)
adam = Adam(learning_rate=0.1)

reduce_lr = ReduceLROnPlateau(
    monitor='loss', factor=0.5, patience=10, min_lr=0.1)

model.compile(loss='categorical_crossentropy',
              optimizer=sgd,
              #optimizer=adam,
              metrics=['accuracy'])

history = model.fit(train,
    epochs=epochs,
    steps_per_epoch=2856//batch_size,
    validation_data=test,
    callbacks=[reduce_lr],
    verbose=1
)


score = model.evaluate(test, verbose=0)

print('Test loss:', score[0])
print('Test accuracy:', score[1])

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
