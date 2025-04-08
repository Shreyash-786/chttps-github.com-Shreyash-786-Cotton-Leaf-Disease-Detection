import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNet
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam

# Define paths to your training and validation datasets
train_data_dir = 'E:/COMPUTER-IT-PROTECH SOL/Nagraj Sir GROUPS/24CP13-Cotton leaf Disease Detection/Code/Cotton Leaf Disease Detection-100% code/Dataset'
validation_data_dir = 'E:/COMPUTER-IT-PROTECH SOL/Nagraj Sir GROUPS/24CP13-Cotton leaf Disease Detection/Code/Cotton Leaf Disease Detection-100% code/Dataset'

# Define image dimensions
img_width, img_height = 224, 224

# Define batch size
batch_size = 32

# Create data generators for training and validation datasets
train_datagen = ImageDataGenerator(
    rescale=1. / 255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True)

validation_datagen = ImageDataGenerator(rescale=1. / 255)

train_generator = train_datagen.flow_from_directory(
    train_data_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode='binary')

validation_generator = validation_datagen.flow_from_directory(
    validation_data_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode='binary')

# Load the MobileNet model without the top layer (include_top=False)
base_model = MobileNet(weights='imagenet', include_top=False)

# Add custom top layers for our binary classification task
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(1024, activation='relu')(x)
predictions = Dense(1, activation='sigmoid')(x)

# Combine base model with custom top layers
model = Model(inputs=base_model.input, outputs=predictions)

# Compile the model
model.compile(optimizer=Adam(lr=0.0001), loss='binary_crossentropy', metrics=['accuracy'])

# Train the model
model.fit_generator(
    train_generator,
    steps_per_epoch=train_generator.samples // batch_size,
    epochs=10,
    validation_data=validation_generator,
    validation_steps=validation_generator.samples // batch_size)

# Save the trained model
model.save('cotton_model1.h5')

# Test the model on a sample image
from tensorflow.keras.preprocessing import image

# Load an image for testing
test_image_path = 'static/images/test_img.png'
test_image = image.load_img(test_image_path, target_size=(img_width, img_height))
test_image = image.img_to_array(test_image)
test_image = np.expand_dims(test_image, axis=0)

# Normalize pixel values
test_image /= 255.

# Predict class probabilities
predictions = model.predict(test_image)

# Map predicted probabilities to class labels
if predictions[0][0] < 0.5:
    print("healthy")
elif predictions[0][1]:
    print("blight disease detected")
elif predictions[0][2]:
    print("curl_virus")

