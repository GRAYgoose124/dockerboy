# -*- coding: utf-8 -*-
"""cifar100.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1zsGo13GXaKF9dovBjxZ-BwK3v8Ph_8lV
"""

import os
import logging
import numpy as np
import tensorflow_datasets as tfds
import tensorflow as tf

# Are we using a GPU?
print("GPU: ", "Avaliable" if tf.config.list_physical_devices(
    'GPU') else "No GPU Accelaration Avaliable!")

# import matplotlib.pyplot as plt

FORCED_REBUILD = True
FORCED_RETRAIN = False

# suppress tensorflow warnings by filtering them out with logging
logging.getLogger('tensorflow').setLevel(logging.ERROR)

# Load the CIFAR-100 dataset
(ds_train, ds_test), ds_info = tfds.load(
    'cifar100',
    split=['train', 'test'],
    shuffle_files=True,
    as_supervised=True,

    with_info=True,
)

# # Prettty prent a relevant subset of ds_info
# def print_ds_info(ds_info):
#     print("* Dataset Info:")
#     print("* Description: ", ds_info.description)
#     print("\n\n* Citation: ", ds_info.citation)
#     print("* Homepage: ", ds_info.homepage)
#     print("* Version: ", ds_info.version)
#     print("* Splits: ", list(ds_info.splits.keys()), ds_info.splits)
#     print("\n* Features: ", ds_info.features)
#     print("\n* Num Classes: ", ds_info.features['label'].num_classes)
#     print("* Class Names: ", ds_info.features['label'].names)

# print_ds_info(ds_info)

# # Define the number of classes in the dataset
num_classes = ds_info.features['label'].num_classes

# Normalize the pixel values of the images


def normalize_image(image, label):
    return tf.cast(image, tf.float32) / 255.0, label


ds_train = ds_train.map(normalize_image)
ds_test = ds_test.map(normalize_image)

# Shuffle and batch the dataset
ds_train = ds_train.shuffle(buffer_size=10000)
ds_train = ds_train.batch(128)
ds_test = ds_test.batch(128)

if os.path.exists(
        'cifar100_trained') and not FORCED_REBUILD and not FORCED_RETRAIN:
    # load the trained model
    model = tf.keras.models.load_model('cifar100_trained')
    print(f"Model Loaded!")
else:
    # Define the model
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(
            128,
            3,
            1,
            activation=tf.nn.relu,
            input_shape=(
                32,
                32,
                3)),
        tf.keras.layers.MaxPool2D(2, 2),
        tf.keras.layers.Conv2D(256, 3, 1, activation=tf.nn.relu),
        tf.keras.layers.MaxPool2D(2, 2),
        tf.keras.layers.Conv2D(128, 3, 1, activation=tf.nn.relu),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(256, activation=tf.nn.relu),
        tf.keras.layers.Dense(64, activation=tf.nn.relu),
        tf.keras.layers.Dense(num_classes, activation=tf.nn.softmax)
    ])

    # Compile the model
    model.compile(
        optimizer='adam',
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=['sparse_categorical_accuracy']
    )

# Tensorboard callbacks
tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir="tb_logs")

# # add image summaries to tensorboard
# class ImageCallback(tf.keras.callbacks.Callback):
#     def __init__(self, log_dir, data):
#         super(ImageCallback, self).__init__()
#         self.log_dir = log_dir
#         self.data = data

#     def on_epoch_end(self, epoch, logs=None):
#         with tf.summary.create_file_writer(self.log_dir).as_default():
#             tf.summary.image("Training data", self.data, max_outputs=25, step=epoch)
# image_callback = ImageCallback("tb_logs", ds_train)

# Train the model
model.fit(
    ds_train,
    epochs=500,
    validation_data=ds_test,
    callbacks=[tensorboard_callback])
tf.keras.models.save_model(model,
                           'cifar100_trained',
                           include_optimizer=True
                           )

model.summary()

# Evaluate the model
results = model.evaluate(ds_test)

# Pretty print evaluation results
print('Test accuracy: {0:.2f}%'.format(results[1] * 100))
print('Test loss: {0:.2f}%'.format(results[0] * 100))
