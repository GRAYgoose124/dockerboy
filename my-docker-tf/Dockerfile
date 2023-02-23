# Use the latest TensorFlow image as the base
FROM tensorflow/tensorflow:latest-gpu

COPY bootstrap.sh /
RUN chmod +x /bootstrap.sh &&\
    "/bootstrap.sh" &&\
    rm -f /bootstrap.sh