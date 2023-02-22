# Use the latest TensorFlow image as the base
FROM tensorflow/tensorflow:latest-gpu

# Install the TensorFlow Datasets library
RUN pip install tensorflow-datasets
