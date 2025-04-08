# -*- coding: utf-8 -*-
import os

import tensorflow as tf

classifierLoad = tf.keras.models.load_model('cotton1model.h5')
import numpy as np
from keras.preprocessing import image


def predict(img_):
    test_image = image.load_img(img_, target_size=(200, 200))
    test_image = np.expand_dims(test_image, axis=0)
    result = classifierLoad.predict(test_image)
    print(result)
    
    if result[0][0] == 1:
        return [" blight leaf disease","Remove infected leaves\nApply fungicide."]
    elif result[0][1] == 1:
        return ["healthy leaf","Maintain proper watering.\nEnsure adequate sunlight."]
    elif result[0][2] == 1:
        return ["Curl_Virus","Remove and destroy infected plants immediately.\nPractice good field sanitation by removing plant debris"]
    
    #if result[0][0] == 1:
    #    return ["Cancer"," "]
    #elif result[0][1] == 1:
    #    return ["Normal"," "]
   


