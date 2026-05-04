import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np

X = np.random.rand(100,128,128,1)
y = np.random.randint(0,8,100)

model = models.Sequential([
    layers.Conv2D(32,(3,3),activation='relu',input_shape=(128,128,1)),
    layers.MaxPooling2D(2,2),
    layers.Conv2D(64,(3,3),activation='relu'),
    layers.MaxPooling2D(2,2),
    layers.Flatten(),
    layers.Dense(128,activation='relu'),
    layers.Dense(8,activation='softmax')
])

model.compile(optimizer='adam',loss='sparse_categorical_crossentropy',metrics=['accuracy'])
model.fit(X,y,epochs=5)

model.save('model/fingerprint_model.h5')
print("Model trained!")