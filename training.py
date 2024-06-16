
import tensorflow as tf
import pandas as pd 
from keras.utils import to_categorical
import random
import numpy as np
import os
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import Input, Lambda, Dense, Flatten, Conv2D, MaxPooling2D, Dropout, Activation, BatchNormalization
from tensorflow.keras.models import Model
from tensorflow.keras.applications.inception_v3 import InceptionV3
from keras.applications.vgg16 import VGG16
from tensorflow.keras.applications.inception_v3 import preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import ImageDataGenerator,load_img, array_to_img, img_to_array
from tensorflow.keras.models import Sequential
from glob import glob

IMAGE_SIZE = [224, 224]

train_path = '/train'
valid_path = '/val'


# #### Inception V3


inception = InceptionV3(input_shape=IMAGE_SIZE + [3], weights='imagenet', include_top=False)


# In[4]:


# We don't need to train existing weights
for layer in inception.layers:
    layer.trainable = False


# In[5]:


# Folders in the Training Set
folders = glob('train/*')
folders


# In[6]:


# Model layers -> can add more if required
x = Flatten()(inception.output)
prediction = Dense(len(folders), activation='softmax')(x)


# In[7]:


# Create a model object
model = Model(inputs=inception.input, outputs=prediction)

# View the structure of the model
model.summary()


# In[8]:


# Defining the cost and model optimization method to use
model.compile(
  loss='categorical_crossentropy',
  optimizer='adam',
  metrics=['accuracy']
)


# In[9]:


# Using the Image Data Generator to import the images from the dataset
from tensorflow.keras.preprocessing.image import ImageDataGenerator

train_datagen = ImageDataGenerator(rescale = 1./255,
                                   shear_range = 0.2,
                                   zoom_range = 0.2,
                                   horizontal_flip = True)

test_datagen = ImageDataGenerator(rescale = 1./255)


# In[10]:


# Training Generator
training_set = train_datagen.flow_from_directory('train',
                                                 target_size = (224, 224),
                                                 batch_size = 32,
                                                 class_mode = 'categorical')


# In[11]:


# Testing Generator
test_set = test_datagen.flow_from_directory('train',
                                            target_size = (224, 224),
                                            batch_size = 32,
                                            class_mode = 'categorical')


# In[12]:


# fit the model, it will take some time to execute
r = model.fit_generator(
  training_set,
  validation_data=test_set,
  epochs=1,
  steps_per_epoch=len(training_set),
  validation_steps=len(test_set)
)


# ## Visualize the model training by plotting Loss Function and Accuracy

plt.plot(r.history['loss'], label='train loss')
plt.plot(r.history['val_loss'], label='val loss')
plt.legend()
plt.show()
plt.savefig('LossVal_loss')

# Accuracy
plt.plot(r.history['accuracy'], label='train acc')
plt.plot(r.history['val_accuracy'], label='val acc')
plt.legend()
plt.show()
plt.savefig('AccVal_acc')


from tensorflow.keras.models import load_model
model.save('imfilter.h5')

y_pred = model.predict(test_set)
y_pred


import numpy as np
y_pred = np.argmax(y_pred, axis=1)
y_pred

